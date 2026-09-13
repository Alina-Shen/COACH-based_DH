#include <cassert>
#include <cstdlib>
#include <string>
#include <libpar/gpi_c.h>
#include <libaview/multi_array.h>
#include <libqints/algorithms/gto/gto_order.h>
#include <libqints/qchem/bagen_1e1c_cgto_qchem.h>
#include <libqints/exec/dev_omp.h>
#include <libgrid/batch/atmcen_grid_batch.h>
#include <libks/drivers/ks_driver_exc.h>
#include <libks/drivers/ks_driver_exc_fxc.h>
#include <libks/drivers/ks_driver_exc_nuc_grad.h>
#include <libks/drivers/ks_driver_exc_nuc_hess.h>
#include <libks/drivers/ks_driver_xc_nuc_grad.h>
#include <libks/drivers/ks_driver_xc_nuc_hess.h>
#include <libks/drivers/ks_driver_fxc_nuc_grad.h>
#include <libks/drivers/ks_driver_fxc_B_grad.h>
#include <libks/drivers/ks_driver_gxc_nuc_grad.h>
#include <libks/drivers/ks_driver_gxc.h>
#include <libks/drivers/ks_driver_hxc.h>
#include <libks/drivers/ks_driver_hxc_nuc_grad.h>
#include <libks/drivers/ks_driver_jxc.h>
#include "import_xcfunc.h"
#include "ks_main.h"

namespace libks {
namespace qchem {
using namespace libaview;
using namespace libqints;

namespace {
bool print_integrated_dv_requested()
{
    const char *value = std::getenv("QCHEM_PRINT_INTEGRATED_DV");
    return value != nullptr && std::string(value) != "0";
}

void check_mem(const size_t mem_total, const size_t mem_req)
{
    std::ostringstream ss;
    ss << "libks needs more memory. "
        << "Please set MEM_TOTAL to " << (size_t)rem_read(REM_MEM_STATIC) + mem_req/1024/1024 + 1 << " or more.";
    if (mem_req > mem_total)
    {
        QCrash(ss.str().c_str());
    }
}

void read_density(unsigned nthreads, const basis_1e1c_cgto<double> &b1,
    size_t nbsf, size_t nb2car, size_t nvec,
    size_t nden, double *p_trial_den, arma::mat &tP, bool do_symmitrize = true, bool do_v2m = true)
{
    if (nvec == 0) return;
    size_t nbsf2 = nbsf * nbsf;
    tP.set_size(nbsf * nbsf * nvec, nden);
    arma::mat tPa(tP.colptr(0), nbsf * nbsf, nvec, false, true);
    arma::mat tPb(tP.colptr(nden - 1), nbsf * nbsf, nvec, false, true);
    #pragma omp parallel for num_threads(nthreads) collapse(2)
    for (size_t iden = 0; iden < nden; iden++)
    for (size_t i = 0; i < nvec; i++)
    {
        if(iden == 0) {
            if (do_v2m) ScaV2M(tPa.colptr(i), p_trial_den + i * nden * nb2car, 1, 1);
            else tPa.col(i) = arma::vec(p_trial_den + i * nden * nbsf2, false, true);
            arma::mat trial_den_tmp(tPa.colptr(i), nbsf, nbsf, false, true);
            gto::reorder_cc(trial_den_tmp, b1, true, true, gto::korder, gto::lex);
            if (!do_symmitrize) continue;
            trial_den_tmp += trial_den_tmp.st();
            trial_den_tmp *= 0.5;
        } else {
            if (do_v2m) ScaV2M(tPb.colptr(i), p_trial_den + i * nden * nb2car + nb2car, 1, 1);
            else tPb.col(i) = arma::vec(p_trial_den + i * nden * nbsf2 + nbsf2, false, true);
            arma::mat trial_den_tmp(tPb.colptr(i), nbsf, nbsf, false, true);
            gto::reorder_cc(trial_den_tmp, b1, true, true, gto::korder, gto::lex);
            if (!do_symmitrize) continue;
            trial_den_tmp += trial_den_tmp.st();
            trial_den_tmp *= 0.5;
        }
    }
}
}


std::pair<size_t, size_t> mem_ks_main_fxc_nuc_grad(const basis_1e1c_cgto<double> &b1,
    const XCFunctional &XCFunc, int grid_type)
{
    double *jCarts;
    INTEGER *iAtNo, NAtoms;
    get_carts(NULL, &jCarts, &iAtNo, &NAtoms, false);
    int blessGhost = rem_read(REM_FIRST_BASISLESS_GHOST);
    if (blessGhost > 0) QCrash("libks does not support Ghost atom when computing Fock matrix derivative. Please contact the support team");
    std::vector<size_t> centers(NAtoms);
    for (size_t i = 0; i < NAtoms; i++) centers[i] = i;
    array_view<size_t> av_centers(&centers[0], centers.size());
    arma::ivec elements(NAtoms);
    arma::mat coord(jCarts, 3, NAtoms);
    for (size_t i = 0; i < elements.n_elem; i++) {
        if (iAtNo[i] == 0) {
            INTEGER IAtNum;
            FileMan(FM_READ, FILE_BASIS_ATOM, FM_INT, 1, i, FM_BEG, &IAtNum);
            elements(i) = IAtNum;
        } else elements(i) = iAtNo[i];
    }
    size_t grid_batch_size = 64;
    if (rem_read(REM_XC_BATCH_SIZE) > 0) grid_batch_size = rem_read(REM_XC_BATCH_SIZE);
    libgrid::atmcen_grid_batch binfo;
    unsigned nthreads = rem_read(REM_THREADS);
    if (binfo.build_grids_no_wts(
            b1, elements, coord, grid_type, 1e-12, nthreads, grid_batch_size, 1.5) != 0)
        throw std::runtime_error("Failed to build grid batches");
    size_t nden = rem_read(REM_JUSTAL) + 1;
    eval_xc xcf;
    if (import_xcfunc(XCFunc, xcf) != 0)
        QCrash("ks_main(): Unsupported XC functional");
    size_t mem_kernel = ks_driver_fxc_nuc_grad::memory_req(nthreads, nden, binfo, xcf);

    size_t nbsf = b1.get_nbsf(), nbsf2 = nbsf * nbsf;
    size_t mem_P = nbsf2 * nden * sizeof(double);
    size_t mem_binfo = binfo.get_ngrid_tot() * 4 * sizeof(double); // coordinate + w0
    size_t mem_fxc_nuc_grad_per_atom = nbsf2 * 3 * sizeof(double) * nden;

    size_t mem_per_atom = mem_fxc_nuc_grad_per_atom;
    size_t mem_independent = mem_kernel + mem_P + mem_binfo;
    return std::make_pair(mem_per_atom, mem_independent);
}

std::pair<size_t, size_t> mem_ks_main_gxc(const libqints::basis_1e1c_cgto<double> &b1,
    const XCFunctional &XCFunc, int grid_type) {
    double *jCarts;
    INTEGER *iAtNo, NAtoms;
    get_carts(NULL, &jCarts, &iAtNo, &NAtoms, false);
    std::vector<size_t> centers(NAtoms);
    for (size_t i = 0; i < NAtoms; i++) centers[i] = i;
    array_view<size_t> av_centers(&centers[0], centers.size());
    arma::ivec elements(NAtoms);
    arma::mat coord(jCarts, 3, NAtoms);
    for (size_t i = 0; i < elements.n_elem; i++) {
        if (iAtNo[i] == 0) {
            INTEGER IAtNum;
            FileMan(FM_READ, FILE_BASIS_ATOM, FM_INT, 1, i, FM_BEG, &IAtNum);
            elements(i) = IAtNum;
        } else elements(i) = iAtNo[i];
    }
    size_t grid_batch_size = 64;
    if (rem_read(REM_XC_BATCH_SIZE) > 0) grid_batch_size = rem_read(REM_XC_BATCH_SIZE);
    libgrid::atmcen_grid_batch binfo;
    unsigned nthreads = rem_read(REM_THREADS);
    if (binfo.build_grids_no_wts(
            b1, elements, coord, grid_type, 1e-12, nthreads, grid_batch_size, 1.5) != 0)
        throw std::runtime_error("Failed to build grid batches");

    size_t nbsf = b1.get_nbsf(), nbsf2 = nbsf * nbsf;
    size_t nden = rem_read(REM_JUSTAL) + 1;
    eval_xc xcf;
    if (import_xcfunc(XCFunc, xcf) != 0)
        QCrash("ks_main(): Unsupported XC functional");
    size_t mem_kernel = ks_driver_gxc::memory_req(nthreads, nden, binfo, nbsf, rem_read(REM_MGGA_GINV), xcf);
    size_t mem_gp_per_vec = nbsf2 * nden * sizeof(double) * 2;
    size_t mem_binfo = binfo.get_ngrid_tot() * 4 * sizeof(double); // coordinate + w0
    size_t mem_P = nbsf2 * nden * sizeof(double);

    size_t mem_per_vec = mem_gp_per_vec;
    size_t mem_independent = mem_kernel + mem_P + mem_binfo;
    return std::make_pair(mem_per_vec, mem_independent);
}

void ks_main(const basis_1e1c_cgto<double> &b1, dftman_adapter& jobinfo,
    const unsigned nthreads, const size_t mem_total)
{
    assert(jobinfo.do_ks);

    // Set up XC functional
    eval_xc xcf;
    if(import_xcfunc(jobinfo.xcfunc, xcf) != 0) {
        QCrash("ks_main(): Unsupported XC functional");
    }
    xcf.cfg("rho_thresh", jobinfo.xc_rho_thresh);
    QTimer Timer;
    if (rem_read(REM_PRINT_XC_TIME) > 0) {
        Timer.On();
    }

    // Set up XC grid batches
    unsigned grid_idrv = 0;
    if (jobinfo.do_exc_nuc_grad || jobinfo.do_fxc_nuc_grad
        || jobinfo.do_gxc_nuc_grad || jobinfo.do_hxc_nuc_grad
        || jobinfo.do_xc_nuc_grad)
    {
        grid_idrv = 1;
    }
    else if (jobinfo.do_exc_nuc_hess || jobinfo.do_xc_nuc_hess)
    {
        grid_idrv = 2;
    }
    // Read molecular system
    double *jCarts;
    INTEGER *iAtNo, NAtoms;
    get_carts(NULL, &jCarts, &iAtNo, &NAtoms, false);
    arma::ivec elements(NAtoms);
    arma::mat coord(jCarts, 3, NAtoms);
    for (size_t i = 0; i < elements.n_elem; i++) {
        if (iAtNo[i] == 0) {
            INTEGER IAtNum;
            FileMan(FM_READ, FILE_BASIS_ATOM, FM_INT, 1, i, FM_BEG, &IAtNum);
            elements(i) = IAtNum;
        } else elements(i) = iAtNo[i];
    }

    libgrid::atmcen_grid_batch ks_binfo;
    if (ks_binfo.build_grids(b1, grid_idrv, elements, coord, jobinfo.grid_type,
        jobinfo.integral_thresh, nthreads, jobinfo.grid_batch_size, jobinfo.shellsize_scale) != 0)
        QCrash("libks::qchem::ks_main(): Error found while building grid points!");

    // Get gto::lex density matrices
    // Note: we DO symmetrize the input density by default because input density
    // matrices are all in packed vector form
    unsigned nden = jobinfo.nden;
    bool is_symm = true;
    const size_t nbsf = b1.get_nbsf(), nbsf2 = nbsf * nbsf;
    arma::mat P;
    read_density(nthreads, b1, nbsf, jobinfo.nb2car, 1, nden, jobinfo.get_den_ptr(), P, is_symm);
    multi_array<double> ma_p(nden);
    ma_p.set(0, array_view<double>(P.colptr(0), P.n_rows));
    ma_p.set(nden - 1, array_view<double>(P.colptr(nden - 1), P.n_rows));

    //  Make list of active atoms for partial/segmented hessian
    size_t ncen = NAtoms;
    std::vector<size_t> active_atoms;
    size_t icen_off = 0, icen_end = ncen - 1;
    if (jobinfo.do_active_atoms_only) {
        icen_off = jobinfo.active_atoms.first;
        icen_end = jobinfo.active_atoms.second;
    }
    for (size_t icen = icen_off; icen <= icen_end; icen++) active_atoms.push_back(icen);
    array_view<size_t> av_act_cen(&active_atoms[0], active_atoms.size());
    size_t nact_cen = active_atoms.size();

    // Prep objects for drivers
    size_t mem_alloc = ks_binfo.get_occ_mem() + P.n_elem * sizeof(double);
    check_mem(mem_total, mem_alloc);
    size_t mem_avail = mem_total - mem_alloc;
    dev_omp dev;
    dev.init(mem_avail / nthreads);
    dev.nthreads = nthreads;

    int rc = 0;
    std::string driver_name;
    //
    //  Call kernel driver according to job type
    //
    if (jobinfo.do_exc && !jobinfo.do_exc_fxc)
    {
        check_mem(mem_avail, ks_driver_exc::memory_req(nthreads, nden, ks_binfo, xcf));
        rc = ks_driver_exc(dev, b1, ks_binfo, jobinfo.integral_thresh, xcf).
            perform(is_symm, ma_p, *jobinfo.get_ec_ptr(), *jobinfo.get_ex_ptr());
        driver_name = std::string("KS_EXC");
    }
    else if (jobinfo.do_exc_fxc)
    {
        arma::mat F(nbsf2, nden);
        multi_array<double> ma_f(nden);
        ma_f.set(0, array_view<double>(F.colptr(0), nbsf2));
        ma_f.set(nden - 1, array_view<double>(F.colptr(nden - 1), nbsf2));
        size_t mem_f = F.n_elem * sizeof(double);
        check_mem(mem_avail, mem_f + ks_driver_exc_fxc::memory_req(nthreads, nden, ks_binfo, xcf));
        double Tol = 1e-4;
        if (jobinfo.grid_type != rem_read(REM_IGRDTY)) Tol *= 100; /* Cut some slack with sleazy grid */
        rc = ks_driver_exc_fxc(dev, b1, ks_binfo, jobinfo.integral_thresh, xcf, rem_read(REM_NALPHA) + rem_read(REM_NBETA), Tol).
            perform(is_symm, ma_p, ma_f, *jobinfo.get_ec_ptr(), *jobinfo.get_ex_ptr());
        if (rc == 0 && print_integrated_dv_requested()) {
            double integrated_dv_Ec = 0.0, integrated_dv_Ex = 0.0;
            check_mem(mem_avail, mem_f + ks_driver_exc::memory_req(nthreads, nden, ks_binfo, xcf));
            rc = ks_driver_exc(dev, b1, ks_binfo, jobinfo.integral_thresh, xcf).
                perform(is_symm, ma_p, integrated_dv_Ec, integrated_dv_Ex);
        }
        arma::mat Fa(F.colptr(0), nbsf, nbsf, false, true);
        gto::reorder_cc(Fa, b1, true, true, gto::lex, gto::korder);
        ScaV2M(Fa.memptr(), jobinfo.get_fxc_ptr(), 1, 0);
        if (nden == 2) {
            arma::mat Fb(F.colptr(1), nbsf, nbsf, false, true);
            gto::reorder_cc(Fb, b1, true, true, gto::lex, gto::korder);
            ScaV2M(Fb.memptr(), jobinfo.get_fxc_ptr() + jobinfo.nb2car, 1, 0);
        }
        driver_name = std::string("KS_EXC_FXC");
    }
    else if (jobinfo.do_exc_nuc_grad)
    {
        check_mem(mem_avail, ks_driver_exc_nuc_grad::memory_req(nthreads, nden, ks_binfo, xcf));
        array_view<double> av_g(jobinfo.get_result_ptr(), ncen * 3);
        rc = ks_driver_exc_nuc_grad(dev, b1, ks_binfo, jobinfo.integral_thresh, xcf).perform(ma_p, av_g);
        driver_name = std::string("KS_EXC_NUC_GRAD");
    }
    else if (jobinfo.do_fxc_nuc_grad)
    {
        arma::mat F_grad(nbsf2 * nact_cen * 3, nden, arma::fill::zeros);
        multi_array<double> ma_f_grad(nden);
        ma_f_grad.set(0, array_view<double>(F_grad.colptr(0), F_grad.n_rows));
        ma_f_grad.set(nden - 1, array_view<double>(F_grad.colptr(nden - 1), F_grad.n_rows));
        size_t mem_f = F_grad.n_elem * sizeof(double);
        check_mem(mem_avail, mem_f + ks_driver_fxc_nuc_grad::memory_req(nthreads, nden, ks_binfo, xcf));
        dev_omp dev0(dev);
        dev0.memory -= mem_f / dev0.nthreads;
        rc = ks_driver_fxc_nuc_grad(dev, b1, ks_binfo, jobinfo.integral_thresh, xcf).perform(av_act_cen, ma_p, ma_f_grad);
        arma::mat Fa_grad(F_grad.colptr(0), nbsf2, nact_cen * 3, false, true);
        arma::mat Fb_grad(F_grad.colptr(nden - 1), nbsf2, nact_cen * 3, false, true);
        #pragma omp parallel for num_threads(dev.nthreads)
        for (size_t i = 0; i < Fa_grad.n_cols; i++)
        {
            arma::mat Fa_grad_i(Fa_grad.colptr(i), nbsf, nbsf, false, true);
            gto::reorder_cc(Fa_grad_i, b1, true, true, gto::lex, gto::korder);
            ScaV2M(Fa_grad_i.memptr(), jobinfo.get_result_ptr() + i * jobinfo.nb2car * nden, 1, 0);
            if(nden == 1) continue;
            arma::mat Fb_grad_i(Fb_grad.colptr(i), nbsf, nbsf, false, true);
            gto::reorder_cc(Fb_grad_i, b1, true, true, gto::lex, gto::korder);
            ScaV2M(Fb_grad_i.memptr(), jobinfo.get_result_ptr() + i * jobinfo.nb2car * nden + jobinfo.nb2car, 1, 0);
        }
        driver_name = std::string("KS_FXC_NUC_GRAD");
    }
    else if (jobinfo.do_exc_nuc_hess)
    {
        check_mem(mem_avail, ks_driver_exc_nuc_hess::memory_req(nthreads, nden, ks_binfo, xcf));
        array_view<double> av_hess(jobinfo.get_result_ptr(), nact_cen * nact_cen * 9);
        rc = ks_driver_exc_nuc_hess(dev, b1, ks_binfo, jobinfo.integral_thresh, xcf).perform(av_act_cen, ma_p, av_hess);
        driver_name = std::string("KS_EXC_NUC_HESS");
    }
    else if (jobinfo.do_xc_nuc_grad)
    {
        // Read trial densities
        arma::mat tP1, tP2;
        read_density(nthreads, b1, nbsf, jobinfo.nb2car, jobinfo.n_trial_vec, nden, jobinfo.get_trial_ptr(), tP1);
        multi_array<double> ma_tp1(nden), ma_tp2(nden);
        ma_tp1.set(0, array_view<double>(tP1.colptr(0), tP1.n_rows));
        ma_tp1.set(nden - 1, array_view<double>(tP1.colptr(nden - 1), tP1.n_rows));
        if (jobinfo.n_trial_vec_2 > 0) {
            read_density(nthreads, b1, nbsf, jobinfo.nb2car, jobinfo.n_trial_vec_2, nden, jobinfo.get_trial_2_ptr(), tP2);
            ma_tp2.set(0, array_view<double>(tP2.colptr(0), tP2.n_rows));
            ma_tp2.set(nden - 1, array_view<double>(tP2.colptr(nden - 1), tP2.n_rows));
        }
        check_mem(mem_avail, ks_driver_xc_nuc_grad::memory_req(nthreads, nden, ks_binfo, xcf));
        array_view<double> av_grad(jobinfo.get_result_ptr(), ncen * 3);
        rc = ks_driver_xc_nuc_grad(dev, b1, ks_binfo, jobinfo.do_triplet_tddft, jobinfo.integral_thresh, xcf).perform(ma_p,
            jobinfo.n_trial_vec, ma_tp1, jobinfo.n_trial_vec_2, ma_tp2, av_grad);
        driver_name = std::string("KS_XC_NUC_GRAD");
    }
    else if (jobinfo.do_xc_nuc_hess)
    {
        // Read trial densities
        arma::mat tP1, tP2;
        read_density(nthreads, b1, nbsf, jobinfo.nb2car, jobinfo.n_trial_vec, nden, jobinfo.get_trial_ptr(), tP1);
        multi_array<double> ma_tp1(nden), ma_tp2(nden);
        ma_tp1.set(0, array_view<double>(tP1.colptr(0), tP1.n_rows));
        ma_tp1.set(nden - 1, array_view<double>(tP1.colptr(nden - 1), tP1.n_rows));
        if (jobinfo.n_trial_vec_2 > 0) {
            read_density(nthreads, b1, nbsf, jobinfo.nb2car, jobinfo.n_trial_vec_2, nden, jobinfo.get_trial_2_ptr(), tP2);
            ma_tp2.set(0, array_view<double>(tP2.colptr(0), tP2.n_rows));
            ma_tp2.set(nden - 1, array_view<double>(tP2.colptr(nden - 1), tP2.n_rows));
        }
        check_mem(mem_avail, ks_driver_xc_nuc_hess::memory_req(nthreads, nden, ks_binfo, xcf));
        array_view<double> av_hess(jobinfo.get_result_ptr(), ncen * ncen * 9);
        rc = ks_driver_xc_nuc_hess(dev, b1, ks_binfo, jobinfo.do_triplet_tddft, jobinfo.integral_thresh, xcf).perform(ma_p,
            jobinfo.n_trial_vec, ma_tp1, jobinfo.n_trial_vec_2, ma_tp2, av_hess);
        driver_name = std::string("KS_XC_NUC_HESS");
    }
    else if (jobinfo.do_gxc)
    {
        //  In case of mGGA gauge invariance, input trial density matrices are in matrix form and not symmetric
        bool do_mgga_ginv = ((xcf.get_type() == libks::eval_xc::MGGA || xcf.get_type() == libks::eval_xc::wMGGA)
            && jobinfo.mgga_ginv_type > 0);
        bool do_symm = is_symm && !do_mgga_ginv;
        arma::mat tP, G(nbsf2, jobinfo.n_trial_vec * nden);
        read_density(nthreads, b1, nbsf, jobinfo.nb2car, jobinfo.n_trial_vec, nden,
            jobinfo.get_trial_ptr(), tP, do_symm, !do_mgga_ginv);
        multi_array<double> ma_tp(nden * jobinfo.n_trial_vec), ma_g(nden * jobinfo.n_trial_vec);
        for (size_t ivec = 0, ii = 0; ivec < jobinfo.n_trial_vec; ivec++)
        for (size_t iden = 0; iden < nden; iden++, ii++) {
            ma_tp.set(ii, array_view<double>(tP.colptr(iden) + nbsf2 * ivec, nbsf2));
            ma_g.set(ii, array_view<double>(G.colptr(ii), G.n_rows));
        }
        check_mem(mem_avail, ks_driver_gxc::memory_req(nthreads, nden, ks_binfo, nbsf, jobinfo.mgga_ginv_type, xcf));
        rc = ks_driver_gxc(dev, b1, ks_binfo, jobinfo.do_triplet_tddft, jobinfo.mgga_ginv_type, jobinfo.integral_thresh, xcf).
            perform(ma_p, jobinfo.n_trial_vec, ma_tp, ma_g);
        #pragma omp parallel for num_threads(nthreads)
        for (size_t ii = 0; ii < nden * jobinfo.n_trial_vec; ii++) {
            arma::mat G_tmp(G.colptr(ii), nbsf, nbsf, false, true);
            gto::reorder_cc(G_tmp, b1, true, true, gto::lex, gto::korder);
            if (do_mgga_ginv) arma::vec(jobinfo.get_result_ptr() + ii * nbsf2, false, true) = G.col(ii);
            else ScaV2M(G_tmp.memptr(), jobinfo.get_result_ptr() + ii * jobinfo.nb2car, 1, 0);
        }
        driver_name = std::string("KS_GXC");
    }
    else if (jobinfo.do_fxc_B_grad)
    {
        arma::mat F_grad(nbsf2 * 3, nden);
        multi_array<double> ma_f_grad(nden);
        ma_f_grad.set(0, array_view<double>(F_grad.colptr(0), F_grad.n_rows));
        ma_f_grad.set(nden - 1, array_view<double>(F_grad.colptr(nden - 1), F_grad.n_rows));
        check_mem(mem_avail, ks_driver_fxc_B_grad::memory_req(nthreads, nden, b1, ks_binfo, xcf));
        rc = ks_driver_fxc_B_grad(dev, b1, ks_binfo, jobinfo.integral_thresh, xcf).perform(ma_p, ma_f_grad);
        arma::mat Fa_grad(F_grad.colptr(0), nbsf2, 3, false, true);
        arma::mat Fb_grad(F_grad.colptr(nden - 1), nbsf2, 3, false, true);
        #pragma omp parallel for num_threads(dev.nthreads)
        for (size_t i = 0; i < Fa_grad.n_cols; i++)
        {
            arma::mat Fa_grad_i(Fa_grad.colptr(i), nbsf, nbsf, false, true);
            gto::reorder_cc(Fa_grad_i, b1, true, true, gto::lex, gto::korder);
            // The following phase-change is required because of the vector form
            for (size_t k = 0; k < nbsf; k++)
            for (size_t j = 0; j < k; j++) Fa_grad_i(j, k) *= -1.0;
            ScaV2M(Fa_grad_i.memptr(), jobinfo.get_result_ptr() + i * jobinfo.nb2car * nden, 1, 0);
            if(nden == 1) continue;
            arma::mat Fb_grad_i(Fb_grad.colptr(i), nbsf, nbsf, false, true);
            gto::reorder_cc(Fb_grad_i, b1, true, true, gto::lex, gto::korder);
            // The following phase-change is required because of the vector form
            for (size_t k = 0; k < nbsf; k++)
            for (size_t j = 0; j < k; j++) Fb_grad_i(j, k) *= -1.0;
            ScaV2M(Fb_grad_i.memptr(), jobinfo.get_result_ptr() + i * jobinfo.nb2car * nden + jobinfo.nb2car, 1, 0);
        }
        driver_name = std::string("KS_FXC_B_GRAD");
    }
    else if (jobinfo.do_hxc)
    {
        // Read trial densities
        arma::mat tP1, tP2;
        read_density(nthreads, b1, nbsf, jobinfo.nb2car, jobinfo.n_trial_vec, nden, jobinfo.get_trial_ptr(), tP1);
        multi_array<double> ma_tp1(nden), ma_tp2(nden);
        ma_tp1.set(0, array_view<double>(tP1.colptr(0), tP1.n_rows));
        ma_tp1.set(nden - 1, array_view<double>(tP1.colptr(nden - 1), tP1.n_rows));
        if (jobinfo.n_trial_vec_2 > 0) {
            read_density(nthreads, b1, nbsf, jobinfo.nb2car, jobinfo.n_trial_vec_2, nden, jobinfo.get_trial_2_ptr(), tP2);
            ma_tp2.set(0, array_view<double>(tP2.colptr(0), tP2.n_rows));
            ma_tp2.set(nden - 1, array_view<double>(tP2.colptr(nden - 1), tP2.n_rows));
        }
        const bool do_same12 = (jobinfo.n_trial_vec_2 == 0);
        size_t ntden = do_same12 ? jobinfo.n_trial_vec : jobinfo.n_trial_vec * jobinfo.n_trial_vec_2;
        arma::mat H(nbsf2 * ntden, nden);
        multi_array<double> ma_h(nden);
        ma_h.set(0, array_view<double>(H.colptr(0), H.n_rows));
        ma_h.set(nden - 1, array_view<double>(H.colptr(nden - 1), H.n_rows));
        check_mem(mem_avail, ks_driver_hxc::memory_req(nthreads, nden, jobinfo.n_trial_vec,
            jobinfo.n_trial_vec_2, do_same12, jobinfo.do_triplet_tddft, jobinfo.do_triplet_tddft_12, ks_binfo, xcf));
        ks_driver_hxc driver(dev, b1, ks_binfo, jobinfo.do_triplet_tddft, jobinfo.do_triplet_tddft_12, jobinfo.integral_thresh, xcf);
        if(do_same12) rc = driver.perform(ma_p, jobinfo.n_trial_vec, ma_tp1, ma_h);
        else rc = driver.perform(ma_p, jobinfo.n_trial_vec, ma_tp1, jobinfo.n_trial_vec_2, ma_tp2, ma_h);
        arma::mat Ha(H.colptr(0), nbsf2, ntden, false, true);
        arma::mat Hb(H.colptr(nden - 1), nbsf2, ntden, false, true);
        #pragma omp parallel for num_threads(nthreads) collapse(2)
        for (size_t iden = 0; iden < nden; iden++)
        for (size_t i = 0; i < ntden; i++)
        {
            double *p = NULL;
            if(iden == 0) p = Ha.colptr(i);
            else p = Hb.colptr(i);
            arma::mat H_tmp(p, nbsf, nbsf, false, true);
            gto::reorder_cc(H_tmp, b1, true, true, gto::lex, gto::korder);
            ScaV2M(p, jobinfo.get_result_ptr() + i * jobinfo.nden * jobinfo.nb2car + iden * jobinfo.nb2car, 1, 0);
            p = NULL;
        }
        driver_name = std::string("KS_HXC");
    }
    else if (jobinfo.do_jxc)
    {
        const bool do_same12 = true;
        const bool do_same123 = false;
        size_t ntden = jobinfo.n_trial_vec * jobinfo.n_trial_vec_2;
        // Read trial densities
        arma::mat tP1, tP2;
        read_density(nthreads, b1, nbsf, jobinfo.nb2car, jobinfo.n_trial_vec, nden, jobinfo.get_trial_ptr(), tP1);
        read_density(nthreads, b1, nbsf, jobinfo.nb2car, jobinfo.n_trial_vec_2, nden, jobinfo.get_trial_2_ptr(), tP2);
        multi_array<double> ma_tp1(nden), ma_tp2(nden);
        ma_tp1.set(0, array_view<double>(tP1.colptr(0), tP1.n_rows));
        ma_tp1.set(nden - 1, array_view<double>(tP1.colptr(nden - 1), tP1.n_rows));
        ma_tp2.set(0, array_view<double>(tP2.colptr(0), tP2.n_rows));
        ma_tp2.set(nden - 1, array_view<double>(tP2.colptr(nden - 1), tP2.n_rows));
        arma::mat J(nbsf2 * ntden, nden);
        multi_array<double> ma_j(nden);
        ma_j.set(0, array_view<double>(J.colptr(0), J.n_rows));
        ma_j.set(nden - 1, array_view<double>(J.colptr(nden - 1), J.n_rows));
        check_mem(mem_avail, ks_driver_jxc::memory_req(nthreads, nden, jobinfo.n_trial_vec,
            jobinfo.n_trial_vec_2, ks_binfo, xcf));
        ks_driver_jxc driver(dev, b1, ks_binfo, jobinfo.do_triplet_tddft, jobinfo.integral_thresh, xcf);
        rc = driver.perform(ma_p, jobinfo.n_trial_vec, ma_tp1, jobinfo.n_trial_vec_2, ma_tp2, ma_j);
        arma::mat Ja(J.colptr(0), nbsf2, ntden, false, true);
        arma::mat Jb(J.colptr(nden - 1), nbsf2, ntden, false, true);
        #pragma omp parallel for num_threads(nthreads) collapse(2)
        for (size_t iden = 0; iden < nden; iden++)
        for (size_t i = 0; i < ntden; i++)
        {
            double *p = NULL;
            if(iden == 0) p = Ja.colptr(i);
            else p = Jb.colptr(i);
            arma::mat J_tmp(p, nbsf, nbsf, false, true);
            gto::reorder_cc(J_tmp, b1, true, true, gto::lex, gto::korder);
            ScaV2M(p, jobinfo.get_result_ptr() + i * jobinfo.nden * jobinfo.nb2car + iden * jobinfo.nb2car, 1, 0);
            p = NULL;
        }
        driver_name = std::string("KS_JXC");
    }
    else if (jobinfo.do_hxc_nuc_grad)
    {
        // Read trial densities
        arma::mat tP;
        multi_array<double> ma_tp(nden);
        read_density(nthreads, b1, nbsf, jobinfo.nb2car, jobinfo.n_trial_vec, nden,
            jobinfo.get_trial_ptr(), tP);
        ma_tp.set(0, array_view<double>(tP.colptr(0), tP.n_rows));
        ma_tp.set(nden - 1, array_view<double>(tP.colptr(nden - 1), tP.n_rows));
        arma::mat H_grad(nbsf2 * ncen * 3 * jobinfo.n_trial_vec, nden);
        multi_array<double> ma_h_grad(nden);
        ma_h_grad.set(0, array_view<double>(H_grad.colptr(0), H_grad.n_rows));
        ma_h_grad.set(nden - 1, array_view<double>(H_grad.colptr(nden - 1), H_grad.n_rows));
        check_mem(mem_avail, ks_driver_hxc_nuc_grad::memory_req(nthreads,
            nden, jobinfo.n_trial_vec, jobinfo.do_triplet_tddft, ks_binfo, xcf));
        rc = ks_driver_hxc_nuc_grad(dev, b1, ks_binfo, jobinfo.do_triplet_tddft,
            jobinfo.integral_thresh, xcf).perform(ma_p, jobinfo.n_trial_vec, ma_tp, ma_h_grad);
        size_t nvec = ncen * 3 * jobinfo.n_trial_vec;
        arma::mat H_grad_tmp(H_grad.memptr(), nbsf2, nvec * nden, false, true);
        #pragma omp parallel for num_threads(dev.nthreads)
        for (size_t i = 0; i < nvec; i++)
        {
            arma::mat Gai(H_grad_tmp.colptr(i), nbsf, nbsf, false, true);
            gto::reorder_cc(Gai, b1, true, true, gto::lex, gto::korder);
            ScaV2M(Gai.memptr(), jobinfo.get_result_ptr() + i * jobinfo.nb2car * nden, 1, 0);
            if (nden == 1) continue;
            arma::mat Gbi(H_grad_tmp.colptr(i + nvec), nbsf, nbsf, false, true);
            gto::reorder_cc(Gbi, b1, true, true, gto::lex, gto::korder);
            ScaV2M(Gbi.memptr(), jobinfo.get_result_ptr() + (i * 2 + 1) * jobinfo.nb2car, 1, 0);
        }
        driver_name = std::string("KS_HXC_NUC_GRAD");
    }
    else if (jobinfo.do_gxc_nuc_grad)
    {
        // Read trial densities
        arma::mat tP;
        multi_array<double> ma_tp(nden);
        read_density(nthreads, b1, nbsf, jobinfo.nb2car, jobinfo.n_trial_vec, nden,
            jobinfo.get_trial_ptr(), tP);
        ma_tp.set(0, array_view<double>(tP.colptr(0), tP.n_rows));
        ma_tp.set(nden - 1, array_view<double>(tP.colptr(nden - 1), tP.n_rows));
        arma::mat G_grad(nbsf2 * ncen * 3 * jobinfo.n_trial_vec, nden);
        multi_array<double> ma_g_grad(nden);
        ma_g_grad.set(0, array_view<double>(G_grad.colptr(0), G_grad.n_rows));
        ma_g_grad.set(nden - 1, array_view<double>(G_grad.colptr(nden - 1), G_grad.n_rows));
        check_mem(mem_avail, ks_driver_gxc_nuc_grad::memory_req(nthreads, nden, jobinfo.n_trial_vec, jobinfo.do_triplet_tddft, ks_binfo, xcf));
        rc = ks_driver_gxc_nuc_grad(dev, b1, ks_binfo, jobinfo.do_triplet_tddft,
            jobinfo.integral_thresh, xcf).perform(ma_p, jobinfo.n_trial_vec, ma_tp, ma_g_grad);
        size_t nvec = ncen * 3 * jobinfo.n_trial_vec;
        arma::mat G_grad_tmp(G_grad.memptr(), nbsf2, nvec * nden, false, true);
        #pragma omp parallel for num_threads(dev.nthreads)
        for (size_t i = 0; i < nvec; i++)
        {
            arma::mat Gai(G_grad_tmp.colptr(i), nbsf, nbsf, false, true);
            gto::reorder_cc(Gai, b1, true, true, gto::lex, gto::korder);
            ScaV2M(Gai.memptr(), jobinfo.get_result_ptr() + i * jobinfo.nb2car * nden, 1, 0);
            if (nden == 1) continue;
            arma::mat Gbi(G_grad_tmp.colptr(i + nvec), nbsf, nbsf, false, true);
            gto::reorder_cc(Gbi, b1, true, true, gto::lex, gto::korder);
            ScaV2M(Gbi.memptr(), jobinfo.get_result_ptr() + (i * 2 + 1) * jobinfo.nb2car, 1, 0);
        }
        driver_name = std::string("KS_GXC_NUC_GRAD");
    }
    else QCrash("Not supported type in libks::qchem::ks_main()");

    if (rc != 0) QCrash("libks::ks_main(): Error found from libks drivers!");

    if (rem_read(REM_PRINT_XC_TIME) > 0) {
        Timer.Off();
        Timer.Print(driver_name.c_str());
    }
}

void ks_main(dftman_adapter& dftman_jobinfo,
    const unsigned nthreads, const size_t mem_total)
{
    basis_1e1c_cgto<double> b1;
    libqints::qchem::bagen_1e1c_cgto_qchem(b1, dftman_jobinfo.bcode);
    ks_main(b1, dftman_jobinfo, nthreads, mem_total);
}

void ks_main(const basis_1e1c_cgto<double> &b1, dftman_adapter& dftman_jobinfo)
{
    dev_omp dev;
    dev.init(100);
    ks_main(dftman_jobinfo, dev.nthreads, (size_t)rem_read(REM_MEM_TOTAL) * (size_t)1024 * 1024);
}

void ks_main(dftman_adapter& dftman_jobinfo)
{
    dev_omp dev;
    dev.init(100);
    basis_1e1c_cgto<double> b1;
    libqints::qchem::bagen_1e1c_cgto_qchem(b1, dftman_jobinfo.bcode);
    ks_main(b1, dftman_jobinfo, dev.nthreads, (size_t)rem_read(REM_MEM_TOTAL) * (size_t)1024 * 1024);
}

bool is_avail_xcfunc(const XCFunctional &XCFunc)
{
    return check_xcfunc(XCFunc);
}

bool is_libks_avail(const int JobNum, const XCFunctional &XCFunc)
{
    if (rem_read(REM_USE_LIBQINTS) == 0) return false;
    if (!check_xcfunc(XCFunc)) return false;
    if (rem_read(REM_XDM) > 0) return false;
    if (rem_read(REM_MRXC) > 0) return false;
    if (rem_read(REM_SRC_DFT) > 0 || rem_read(REM_INCDFT) > 0) return false;
    if (rem_read(REM_CDFTCI_FRAGMENT) > 0 || rem_read(REM_CDFTCI) > 0) return false;
    if (rem_read(REM_IGRDTY) < 0) return false;
    if (rem_read(REM_SAPT_CDFT_EDA) > 0) return false;
    if (JobNum == XCENERGY_ONLY) return false;
    if (rem_read(REM_CDFT_BECKE_POP_TMP) > 0) return false;  // NYI in libgrid
    if (XCFunc.HasLap()) return false;
    bool do_tddft = (JobNum == IMPLICIT_1STDRV_OF_XCMTRX || JobNum == IMPLICIT_2NDDRV_OF_XCMTRX
        || JobNum == IMPLICIT_3NDDRV_OF_XCMTRX || JobNum == EXPLICIT_NUC_2NDDRV_OF_XC
        || JobNum == EXPLICIT_NUC_1STDRV_OF_GXC || JobNum == EXPLICIT_NUC_1STDRV_OF_KERNAL
        || JobNum == EXPLICIT_NUC_1STDRV_OF_XC);
    if (do_tddft && rem_read(REM_WANG_ZIEGLER_KERNEL) > 0) return false;
    if (rem_read(REM_GVB_DFT_DO) == 1) return false;
    //if (GPI_nproc() > 1) return false; // MPI - commented out by Kaushik

    if (JobNum == XCMTRX) {
        if (rem_read(REM_XC_FXC) >= 0 && rem_read(REM_XC_FXC) != 3) return false;
    }
    if (JobNum == EXPLICIT_NUC_1STDRV_OF_XCENERGY) {
        if (rem_read(REM_XC_D1E) >= 0 && rem_read(REM_XC_D1E) != 3) return false;
    }
    if (JobNum == EXPLICIT_NUC_1STDRV_OF_XCMTRX) {
        if (rem_read(REM_XC_D1FXC) >= 0 && rem_read(REM_XC_D1FXC) != 3) return false;
    }
    if (JobNum == IMPLICIT_1STDRV_OF_XCMTRX) {
        if (rem_read(REM_XC_FXCM) >= 0 && rem_read(REM_XC_FXCM) != 3) return false;
    }
    if (JobNum == EXPLICIT_NUC_2NDDRV_OF_XCENERGY) {
        if (rem_read(REM_XC_D2E) >= 0 && rem_read(REM_XC_D2E) != 3) return false;
    }
    if (JobNum == EXPLICIT_NUC_1STDRV_OF_GXC) {
        if (rem_read(REM_XC_D1GXC) >= 0 && rem_read(REM_XC_D1GXC) != 3) return false;
    }
    if (JobNum == IMPLICIT_2NDDRV_OF_XCMTRX) {
        if (rem_read(REM_XC_HXC) >= 0 && rem_read(REM_XC_HXC) != 3) return false;
    }
    if (JobNum == IMPLICIT_3NDDRV_OF_XCMTRX) {
        if (rem_read(REM_XC_JXC) >= 0 && rem_read(REM_XC_JXC) != 3) return false;
    }
    if (JobNum == EXPLICIT_NUC_1STDRV_OF_KERNAL) {
        if (rem_read(REM_XC_D1FXCM) >= 0 && rem_read(REM_XC_D1FXCM) != 3) return false;
    }
    if (JobNum == EXPLICIT_NUC_2NDDRV_OF_XC) {
        if (rem_read(REM_XC_D2XC) >= 0 && rem_read(REM_XC_D2XC) != 3) return false;
    }
    if (JobNum == EXPLICIT_NUC_1STDRV_OF_XC) {
        if (rem_read(REM_XC_D1XC) >= 0 && rem_read(REM_XC_D1XC) != 3) return false;
    }
    if (JobNum == EXPLICIT_BFIELD_1STDRV_OF_XCMTRX) {
        if (rem_read(REM_XC_FXCB) >= 0 && rem_read(REM_XC_FXCB) != 3) return false;
    }

    return true;
}

} // qchem
} // libks
