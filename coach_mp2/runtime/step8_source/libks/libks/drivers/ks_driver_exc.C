#include <libgrid/eval_screen_basis.h>
#include <libks/exc_fxc/exc_fxc.h>
#include <libks/exc_fxc/integrated_dv.h>
#include <libks/exc_fxc/mgga_DFV.h>
#include <libks/utils/utils.h>
#include <libqints/arrays/arrays.h>
#include <cassert>
#include <cstdint>
#include <cstdlib>
#include <fstream>
#include <iomanip>
#include <string>
#include "ks_driver_exc.h"

namespace libks
{
using namespace libqints;

ks_driver_exc::ks_driver_exc(
    const dev_omp &dev, const basis_1e1c_cgto<double> &b1, const libgrid::grid_batch_info &ks_binfo, double thresh, eval_xc &xcf)
    : m_thresh(thresh), m_dev(dev), m_b1(b1), m_ks_binfo(ks_binfo), m_xcf(xcf) {
    m_srt_idx = ks_binfo.get_srt_keys();
    if (m_srt_idx.n_elem != ks_binfo.get_nbatch())
        m_srt_idx = arma::linspace<arma::uvec>(0, ks_binfo.get_nbatch() - 1, ks_binfo.get_nbatch());
}

int ks_driver_exc::perform(const bool is_symm, const multi_array<double> &ma_den, double &Ec, double &Ex) {
    // Initialize objects and check sizes
    const size_t nbat = m_ks_binfo.get_nbatch();
    const size_t nbsf = m_b1.get_nbsf(), nbsf2 = nbsf * nbsf;
    const size_t nden = ma_den.get_n_arrays();
    const bool unrestricted = (nden == 2);
    assert(nbat == m_srt_idx.n_elem);
    assert(nden <= 2 && nden > 0);
    assert(ma_den[0].size() == nbsf2 && ma_den[nden - 1].size() == nbsf2);

    // COACH feature export is deliberately opt-in so production Q-Chem behavior
    // is unchanged unless the workflow explicitly requests integratedDV output.
    const char *integrated_dv_env = std::getenv("QCHEM_PRINT_INTEGRATED_DV");
    const bool print_integrated_dv = integrated_dv_env != nullptr && std::string(integrated_dv_env) != "0";
    const char *diagnostic_path_env = std::getenv("QCHEM_DUMP_INTEGRATED_DV_INPUTS");
    const bool dump_integrated_dv_inputs = diagnostic_path_env != nullptr && std::string(diagnostic_path_env).size() > 0;
    if (print_integrated_dv && m_xcf.get_type() != eval_xc::MGGA) {
        std::cerr << " QCHEM_PRINT_INTEGRATED_DV requires an MGGA density functional." << std::endl;
        return 1;
    }
    if (dump_integrated_dv_inputs && !print_integrated_dv) {
        std::cerr << " QCHEM_DUMP_INTEGRATED_DV_INPUTS requires QCHEM_PRINT_INTEGRATED_DV." << std::endl;
        return 1;
    }

    std::ofstream diagnostic_stream;
    bool diagnostic_write_failed = false;
    if (dump_integrated_dv_inputs) {
        std::ifstream existing(diagnostic_path_env, std::ios::binary);
        if (existing.good()) {
            std::cerr << " Refusing to overwrite integratedDV diagnostic input file: "
                      << diagnostic_path_env << std::endl;
            return 1;
        }
        diagnostic_stream.open(diagnostic_path_env, std::ios::binary | std::ios::out);
        if (!diagnostic_stream.good()) {
            std::cerr << " Cannot open integratedDV diagnostic input file: "
                      << diagnostic_path_env << std::endl;
            return 1;
        }
        diagnostic_stream.write("COACHDV1", 8);
    }

    // Check memory requirement
    std::stringstream ss;
    size_t mem_req = memory_req(m_dev.nthreads, nden, m_ks_binfo, m_xcf, ss);
    {
        if (mem_req > m_dev.memory * m_dev.nthreads) {
            print_mem_MB("ks_driver_exc::perform()", mem_req, std::cout);
            std::cout << ss.str() << std::endl;
            std::cout << "ks_driver_exc(): Please increase MEM_TOTAL!" << std::endl;
            return 1;
        }
    }

    // Prep objects in parallel section
    bool do_chi1 = (m_xcf.get_type() == eval_xc::GGA || m_xcf.get_type() == eval_xc::MGGA);
    size_t Chi_drv = do_chi1 ? 1 : 0;
    size_t ndc = do_chi1 ? 4 : 1;
    Ec = 0.0;
    Ex = 0.0;
    arma::mat Pa_full(arrays<double>::ptr(ma_den[0]), nbsf, nbsf, false, true);
    arma::mat Pb_full(arrays<double>::ptr(ma_den[nden - 1]), nbsf, nbsf, false, true);
    arma::mat integrated_dv;
    if (print_integrated_dv)
        integrated_dv.zeros(integrated_dv_rows, integrated_dv_cols);

    //
    // Loop all grid batches in OpenMP parallel section
    //
#pragma omp parallel for num_threads(m_dev.nthreads) schedule(dynamic, GRANULARITY)
    for (size_t ib = 0; ib < nbat; ib++) {
        // Get dimension of current grid batch
        size_t ibat = m_srt_idx(ib);
        size_t ngrid_bat = m_ks_binfo.get_ngrid(ibat);
        if (ngrid_bat == 0) continue;

        //  Compute and screen basis functions on grids.
        arma::mat Chi_scr;
        arma::uvec Isig;
        {
            //  Allocate memory from buffer, note: the results will be in Chi_unscr
            const size_t nbsf_bat = m_ks_binfo.get_nbsf_from_sig_atom(ibat);
            Chi_scr.set_size(ngrid_bat, nbsf_bat * ndc);
            arma::mat grid_coord(ngrid_bat, 3);
            m_ks_binfo.get_grid_pts(ibat, grid_coord, false);
            libgrid::eval_screen_basis(1, m_b1, m_ks_binfo.get_sig_shell_list(ibat), Chi_drv, grid_coord, m_thresh, Chi_scr, Isig);
        }
        size_t nsig = Isig.n_elem, nsig2 = nsig * nsig;
        if (nsig == 0) continue;
        //  The evaluated screened basis starts from the current memory offset
        Chi_scr.resize(ngrid_bat, nsig * ndc);

        // Extract weight
        arma::vec w0(ngrid_bat);
        m_ks_binfo.get_grid_wts(ibat, w0);

        // Screen density matrices
        arma::mat Pa_scr(nsig, nsig), Pb_scr;
        utils::screen_density_matrix(nbsf, Pa_full, nsig, Isig, Pa_scr);
        double Pnorm = arma::norm(Pa_scr, "fro");
        if (unrestricted) {
            Pb_scr.set_size(nsig, nsig);
            utils::screen_density_matrix(nbsf, Pb_full, nsig, Isig, Pb_scr);
            Pnorm += arma::norm(Pb_scr, "fro");
        }
        if (Pnorm < 1e-30) continue;

        // Call kernels
        arma::mat buff(ngrid_bat, get_nbuff_exc(nsig, nsig, m_xcf));
        double Ec_thd = 0.0, Ex_thd = 0.0;
        eval_exc(buff, ngrid_bat, nsig, nsig, w0, Chi_scr, Chi_scr, unrestricted, is_symm, Pa_scr, Pb_scr, m_xcf, Ec_thd, Ex_thd);

        arma::mat integrated_dv_batch, integrated_dv_diagnostic_batch;
        if (print_integrated_dv) {
            arma::mat dfv(ngrid_bat, 10);
            arma::mat Chi0(Chi_scr.colptr(0), ngrid_bat, nsig, false, true);
            arma::mat Chi1(Chi_scr.colptr(nsig), ngrid_bat, 3 * nsig, false, true);
            if (is_symm) {
                arma::mat dfv_buff(ngrid_bat, get_nbuff_mgga_DFV(nsig));
                if (unrestricted)
                    mgga_u_DFV(dfv_buff, ngrid_bat, nsig, Chi0, Chi1, Pa_scr, Pb_scr, dfv);
                else
                    mgga_r_DFV(dfv_buff, ngrid_bat, nsig, Chi0, Chi1, Pa_scr, dfv);
            } else {
                arma::vec Rhoa(dfv.colptr(0), ngrid_bat, false, true);
                arma::vec Rhob(dfv.colptr(1), ngrid_bat, false, true);
                arma::mat Rhoa1(dfv.colptr(2), ngrid_bat, 3, false, true);
                arma::mat Rhob1(dfv.colptr(5), ngrid_bat, 3, false, true);
                arma::vec Taua(dfv.colptr(8), ngrid_bat, false, true);
                arma::vec Taub(dfv.colptr(9), ngrid_bat, false, true);
                arma::mat dfv_buff(ngrid_bat, get_nbuff_mgga_DFV(nsig, nsig));
                mgga_DFV(dfv_buff, ngrid_bat, nsig, nsig,
                    Chi0, Chi1, Chi0, Chi1,
                    Pa_scr, Rhoa, Rhoa1, Taua);
                if (unrestricted) {
                    mgga_DFV(dfv_buff, ngrid_bat, nsig, nsig,
                        Chi0, Chi1, Chi0, Chi1,
                        Pb_scr, Rhob, Rhob1, Taub);
                } else {
                    Rhob = Rhoa;
                    Rhob1 = Rhoa1;
                    Taub = Taua;
                }
            }

            integrated_dv_batch.set_size(integrated_dv_rows, integrated_dv_cols);
            arma::vec Rhoa(dfv.colptr(0), ngrid_bat, false, true);
            arma::vec Rhob(dfv.colptr(1), ngrid_bat, false, true);
            arma::mat Rhoa1(dfv.colptr(2), ngrid_bat, 3, false, true);
            arma::mat Rhob1(dfv.colptr(5), ngrid_bat, 3, false, true);
            arma::vec Taua(dfv.colptr(8), ngrid_bat, false, true);
            arma::vec Taub(dfv.colptr(9), ngrid_bat, false, true);
            eval_integrated_dv(ngrid_bat, w0, Rhoa, Rhob, Rhoa1, Rhob1, Taua, Taub, integrated_dv_batch);
            if (dump_integrated_dv_inputs) {
                integrated_dv_diagnostic_batch.set_size(ngrid_bat, 11);
                integrated_dv_diagnostic_batch.col(0) = w0;
                integrated_dv_diagnostic_batch.cols(1, 10) = dfv;
            }
        }
#pragma omp critical
        {
            Ec += Ec_thd;
            Ex += Ex_thd;
            if (print_integrated_dv) integrated_dv += integrated_dv_batch;
            if (dump_integrated_dv_inputs) {
                const std::uint64_t diagnostic_rows = static_cast<std::uint64_t>(ngrid_bat);
                diagnostic_stream.write(reinterpret_cast<const char *>(&diagnostic_rows), sizeof(diagnostic_rows));
                diagnostic_stream.write(
                    reinterpret_cast<const char *>(integrated_dv_diagnostic_batch.memptr()),
                    static_cast<std::streamsize>(integrated_dv_diagnostic_batch.n_elem * sizeof(double)));
                if (!diagnostic_stream.good()) diagnostic_write_failed = true;
            }
        }
    }  // for()

    if (print_integrated_dv) {
        std::ios::fmtflags old_flags = std::cout.flags();
        std::streamsize old_precision = std::cout.precision();
        std::cout << " COACH integratedDV begin rows=" << integrated_dv_rows
                  << " cols=" << integrated_dv_cols << std::endl;
        std::cout << std::scientific << std::setprecision(16);
        integrated_dv.raw_print(std::cout, "integratedDV");
        std::cout.flags(old_flags);
        std::cout.precision(old_precision);
        std::cout << " COACH integratedDV end" << std::endl;
    }
    if (dump_integrated_dv_inputs) {
        const std::uint64_t end_marker = 0;
        diagnostic_stream.write(reinterpret_cast<const char *>(&end_marker), sizeof(end_marker));
        diagnostic_stream.close();
        if (diagnostic_write_failed || !diagnostic_stream) {
            std::cerr << " Failed while writing integratedDV diagnostic input file: "
                      << diagnostic_path_env << std::endl;
            return 1;
        }
    }

    return 0;
}

size_t ks_driver_exc::memory_req(const unsigned nthreads, const size_t nden, const libgrid::grid_batch_info &ks_binfo, const eval_xc &xcf, std::ostream &os) {
    const size_t nbatch = ks_binfo.get_nbatch();
    unsigned Chi_drv = 0, ndc = 1;
    if (xcf.get_type() == eval_xc::GGA || xcf.get_type() == eval_xc::MGGA) {
        Chi_drv = 1;
        ndc = 4;
    }
    std::vector<size_t> srt_mem;
    size_t max_nbsf_bat, max_ngrid_bat, max_mem_bat = 0;
    for (size_t ibat = 0; ibat < nbatch; ibat++) {
        size_t ngrid = ks_binfo.get_ngrid(ibat);
        if (ngrid == 0) continue;
        size_t nbsf_bat = ks_binfo.get_nbsf_from_sig_atom(ibat);

        // Memory for w0
        size_t mem_w0 = ngrid;
        // Memory for evaluate basis
        size_t mem_eval_basis = ngrid * 3;
        // Memory for Chi
        size_t mem_Chi = ngrid * nbsf_bat * ndc;
        //  Memory for density matrices
        size_t mem_P = nbsf_bat * nbsf_bat;
        if (nden == 1)
            mem_P += 4;
        else
            mem_P *= 2;
        // Memory for kernel buffer vectors
        size_t mem_kernel = ngrid * get_nbuff_exc(nbsf_bat, nbsf_bat, xcf);

        //  Memory for step 1: Evaluating basis
        size_t mem_step1 = mem_Chi + mem_eval_basis;
        //  Memory for step 2: Run kernels
        size_t mem_step2 = mem_Chi + mem_P + mem_kernel;

        //  Memory for this batch
        size_t mem_bat = mem_w0 + std::max(mem_step1, mem_step2);
        add_to_sorted_list(nthreads * GRANULARITY, srt_mem, mem_bat);

        //  Save info for print outs
        if (mem_bat > max_mem_bat) {
            max_mem_bat = mem_bat;
            max_nbsf_bat = nbsf_bat;
            max_ngrid_bat = ngrid;
        }
    }
    size_t mem_need = 0;
    for (size_t idx = 0; idx < srt_mem.size(); idx += GRANULARITY) mem_need += srt_mem[idx];
    mem_need *= sizeof(double);
    os << " Memory required per thread for computing Kohn Sham DFT part of E is " << mem_need / ((size_t)nthreads * 1024 * 1024)
       << " MB" << std::endl;
    os << " In the largest grid batch:" << std::endl;
    os << "  The number of grid points: " << max_ngrid_bat << std::endl;
    os << "  The number of estimated significant basis functions: " << max_nbsf_bat << std::endl;
    return mem_need;
}

size_t ks_driver_exc::memory_req(
    const unsigned nthreads, const size_t nden, const libgrid::grid_batch_info &ks_binfo, const eval_xc &xcf) {
    std::stringstream ss;
    return memory_req(nthreads, nden, ks_binfo, xcf, ss);
}

}  // namespace libks
