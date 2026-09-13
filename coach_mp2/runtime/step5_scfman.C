/*    Confidential property of Q-Chem, Inc.

Copyright (c) 1993 by Q-Chem, Inc. (unpublished)
All rights reserved.

The above copyright notice is intended as a precaution against
inadvertent publication and does not imply publication or any
waiver of confidentiality. The year included in the foregoing
notice is the year of creation. This software product contains
proprietary, confidential information and trade secrets of
Q-Chem, Inc. and its licensors. No use may be made of this
software except according to written agreement with Q-Chem, Inc.  */

#include "qcio.h"
#include "qcmath.h"
#include <stdio.h>
#include <iostream>
#include <stdlib.h>
#include <string.h>
#include "qchem.h"
#include "integrals.h"
#include "functionals.h"
#include "BSetMgr.hh"
#include "DIISController.h"
// JKN: effective disk-storage
#include "DIISControllerCS.h"
#include "SCFConvControl.h"
#include "OneEMtrx.hh"
#include "MultipoleField.h"
#include "PointCharges.h"
#include "GUI.h"
#include "scfman.h"
#include "mom.h"
#include "Parallel.h"
#include "local_interp.h"
#include "scf2.h"
#include "SVPInfo.h"
//RST: add some headers
#include "fragment.h"
#include "NVOstep.h"
//EndRST
#include "dual.h"
#include "BasisType.h"
#include "DynamicDispatcher.h"
#include "operators.h"  // For long-range exchange stuff, aka LRK (TD 2/06)
#include "LRK_init.h"
#include "efpman2/EFP2.h"
#include "cdft.h"
#include "cdft_ci.h"
#include "rem_values.h"
#include "xpol.h"
#include "xpolman.h"
#include "mbeman.h"
#include "roks.h"
#include "../forceman/forceman_class.h"
#include "../forceman/forceman.h"
#include <libscrf/scrf.h>
#include <libscrf/pcm/pcm_jobtype.h>
#include <libsmx/libsmx.h>
#include <libdf/qchem/occrik_libdf.h>
#include "libvdw.h"
#include "step.h"
#include "step_scfman.h"
#include <libmdc/threading_policy.h>
#include <libqchem/tasks/basic_display.h>
#include <anlman/qink_anlman.h>
#include <libarchive/qchem/qarchive_scfman.h>

using namespace libarchive::impl;

#define JMHDEBUG 0

//AJWT Searching for multiple SCF minima
#include "SCFMinFind.h"
#ifdef JKN
void sparsity2(double *, int, int, int, double *, double *, char *);
#endif

extern void den2MO(double* MOs, const GenMatrix& P, const double* X,
		   const BasisSet& s1, INTEGER nbasis, INTEGER norb);

// Trans code
int  transcpp_main(int,int,int,int, double*, double*, double*, double*, double*,int,int,int);
void trans_get_Vbias(double*, int*,const std::string&);
void trans_NEGF_cleanup_files();
void rw_disc_trans_6_double(double*,double*,double*,double*,double*,double*,const char*,const std::string&);
void rw_disc_trans_1D_double(double*,int,const char*,const std::string&);
void rw_disc_trans_FSDmat(int,int,double*,double*,double*,double*,double*,int*,bool,const char*);
void modify_fock_negf(int,int,int,int, double*,double*,double*,double*,double*, int);
void update_DmatLR(int,int,double*,double*,double*,double*,int,int);
void read_restart_NEGF_files(int,int,double*,double*,double*,double*,double*);
void print_transmission_tdos(int, int,int,int,int,int*,double*,double*,double*,double*,double*,const std::string&);
void files_NEGF_after_conv(int,int);

//njm for printing corresponding unpaired orbitals
#include <DevKeyword.h>
#include <GUI.h>
void get_corresponding_orbs();

//Scale_by_dielectric declaration
void Scale_by_dielectric(double[], double[], int, int, int, int, int);
INTEGER IDC1, IDC2, InterM, inter_basis=-1;

extern double empirical_dispersion(void);
extern double airbed(void);

extern LOGICAL CanUseIntsStorageSCF();
extern "C" void orimo(double* V, INTEGER* I);
void HFPTman();
void AddFractionalElectron(double*,double*);
extern "C" void add_frac_elec(double*,double*,INTEGER*,INTEGER*,double*);
extern double QMMMFock(double* jS, double* jFAv,double* jFBv, double* jPAv,double* jPBv,int NBasis,int NDen,bool FileWritten,double* jQj);

/*
 * Local helper routines for SCFman.
 * Use these to help keep the main SCFman() routine short and (hopefully)
 * readable.
 */
static void scfman_read_guess_density(bool use_Pv, INTEGER NDen,
    double *jPAv, double *jPBv, double *jPA, double *jPB);

/******************************************************************
 *                                                                *
 *               SCFman manages an SCF calculation.               *
 *                                                                *
 *               PMWG (2/93)                                      *
 *               BGJ  (4/93)                                      *
 *               MHG  (7/93)                                      *
 *                                                                *
 ******************************************************************/
#include "../libdft/vdwdata.h"

void SCFman(INTEGER& NDen, INTEGER& IPrint, const XCFunctional& XCFunc0, INTEGER KonSCF)
{
   bool isXPol = (rem_read(REM_XPOL) == 1) ? true : false;

   bool ri_comb_k = (rem_read(REM_PARI_K) || rem_read(REM_IARI_K)) ;
   if((rem_read(REM_OCC_RI_K) == 1 || rem_read(REM_RI_K) == 1)) {
      if(rem_read(REM_USE_LIBQINTS) == 0) rem_write(0,REM_COMBINE_K);
   }

   if(rem_read(REM_OCC_RI_K) == 1 && rem_read(REM_USE_LIBQINTS) != 0) {
      libdf::qchem::occrik_libdf().init();
   }

   // DFT general setting XCFunc & Grid
   XCFunctional XCFunc=XCFunc0;
   if (XCFunc.IsComplex()) QCrash("SCFman cannot handle complex-variable XC functionals!");
   INTEGER IGrdDF_2;

   // XDM for DFT
   //   Use modify XCFunc if the job is to compute VDW
   //   The reason to use a temp. XCFunc object:
   //   1. The analytical hessian forbids the use of Tau or Lap dependent functionals,
   //      so the input xc_functional can not contain BR89_VDW, otherwise, the program
   //      switches to numerical hessian automatically.
   //   2. However, to run dftman with VDW, XCFunc must be constructed including BR89_VDW.
   //   3. We must build XCFunc here instead in dftman because some initial settings
   //      depend on if VDW (or tau, lap, etc.) functionals are available or not
   //
   // create vdwdata global object
   //
   VDWData* vdwdata = getVDWDataPtr();
   if ( vdwdata == NULL ) {
        #ifdef DEVELOPMENT
           printf(" Initialize XDM data structure\n");
        #endif
        vdwdata = iniVDWDataPtr();
   }
   //vdw data ptr is out of style each time scfman is called with new fragment
   else if (rem_read(REM_OMEGA_GDD) == 1 && rem_read(REM_OMEGA_GDD_VALUE) > 0){
      delVDWDataPtr();
      vdwdata = iniVDWDataPtr();
   }
   else if (isXPol)
   {
      delVDWDataPtr();
      vdwdata = iniVDWDataPtr();
   }
   else if (rem_read(REM_HIRSHITER) == 1){  //KAUN
      delVDWDataPtr();
      vdwdata = iniVDWDataPtr();
   }
   else if (rem_read(REM_MANY_BODY_INT) == 1){ //KAUN
      delVDWDataPtr();
      vdwdata = iniVDWDataPtr();
   }
   else if (rem_read(REM_MBE_BSSE_ORDER) > 0){ //KAUN
      delVDWDataPtr();
      vdwdata = iniVDWDataPtr();
   }
   else if (rem_read(REM_FRAG_MOL_ORB)){//KAUN
      delVDWDataPtr();
      vdwdata = iniVDWDataPtr();
   }
   else if (rem_read(REM_FDE) == TRUE){//AZ
      delVDWDataPtr();
      vdwdata = iniVDWDataPtr();
   }
   if ( vdwdata->getVDWJob() !=0 && ! XCFunc.HasVDW() ) {
       XCFunc.AddC(CFUNC_VDW_BR89,1.0);
       XCFunc.setType();
   }
   // postpone XDM calculation until SCF converged unless performing XDM in SCF way
   int  vdwJob = rem_read(REM_XDM);
   if ( vdwJob == 1 ) vdwdata->vdwJob = 0;


#ifdef RUSTY
  //RST: time scf
  qtime_t rusty00;
  double rusty01[3];
  rusty00 = QTimerOn();
  //endRST
#endif

  int trans_enable;
  trans_enable = rem_read(REM_TRANS_ENABLE);
  // =1 get into the transport analysis; =-1 only print!

  if(rem_read(REM_SEMI_EMPIRICAL) == 1) {
    SCFman_semi();
    return;
  }
  double *jTop = qalloc_double(0);

  //JDC
  double *Ets   = qalloc_double(1);
  double *Theta = qalloc_double(1);
  double *Ets_fake = qalloc_double(1);
  double Itheta = 0.0;
#ifdef REM_TAO_DFT
#ifdef REM_TAO_DFT_THETA_NDP
  Itheta = rem_read(REM_TAO_DFT_THETA)*TenMin(rem_read(REM_TAO_DFT_THETA_NDP));
#else
  Itheta = rem_read(REM_TAO_DFT_THETA)/1000.0;
#endif
#endif
  VRload(Theta,1,Itheta);
  VRload(Ets,1,0.0);
  VRload(Ets_fake,1,0.0);
  double EtsA, EtsB;
  EtsA=0.0;
  EtsB=0.0;

  INTEGER JustAl,NAlpha,NBeta,NBasis,NBas6D,NB2,
    NB2car,NOrb,MaxSCF,MetSCF,IGrdDF,MetDIIS,N,N2,ItDM,NOA,NOB,NVA,NVB,
    NTheta,NMO,IteSCF,L,i,NBadDIIS,IThrDIIS,CurDIIS,TotDIIS,NSS,ItRCA,
    NBadRCA,IThrRCA, Quad_not_Conv,roks_a,roks_b;
  INTEGER MetNEGF=0;
  int    iVbias=-1,tran_opt=0, tran_restart=0;
  double Cnverg_NEGF, Vbias;
  double Cnverg,ET,E1,EJ,EKA,EKB,EX(0.),EC(0.),EKAsr,EKBsr,
    ETot,EMax,EV,ECou,EOld,DEMax,EOpSing,ESing,
    t[10],*jTh,*jGr,EXC, EKirkwood,
    Step,Curv,EOld0,GRMS,Edisp,Eairbed,ScaleLR,ScaleSR;
  double EewQMMM=0.0;
  double xETot(0.0),xpMinE(0.0),xpElecMull(0.0),xpNucMull(0.0);
  double xpElecExt=0.0,xpNucExt=0.0,fmoElecDen=0.0,fmoMinE=0.0;
  double eNucSolvnt(0.0), eSolvnt(0.0);
  double eNucSolvnt_old=0., eSolvnt_old=0.;
  double ThrDIIS,ThrRCA;
  //ConvOK shows that on the given SCF cycle if convergence criteria are satisfied,
  //the wavefunctiuon may considered to be converged.  It is T for everything but GDIIS step
  //in GDIIS
  LOGICAL usingDM,canUseDM,usingGDM,canUseGDM,usingNEGF,usingGDIIS,canUseGDIIS,DoJ,NoSCF,ConvOK,
          ExtrapFock,BuildFock,MP2Restart,add_LRK,UseRCA,MOMFroz;
  qtime_t t0, tdE, tdf2m, tdC, tdnegf;
  double t1[3], t2[3], t3[3], BuildTime=0.0;
  double *jPA=NULL,*jPB=NULL,*jKA=NULL,*jKB=NULL,*jFA=NULL,*jFB=NULL,
    *jKAsr=NULL,*jKBsr=NULL,*jCA=NULL,*jCB=NULL,*jEA=NULL,*jEB=NULL,
    *jPAv,*jPBv,*jJv_temp=NULL,*jJv,*jXCAv,*jXCBv,*jFAv,*jFBv,*jS,
    *jxRCA=NULL, *jARCA=NULL, *jERCA=NULL, *jE0RCA=NULL,
    *jdxRCA=NULL, *jgxRCA=NULL, *jPvPCM=NULL, *jE_PCM=NULL, *jQj=NULL;
  cdft_data *jCDFT = NULL;
  double Epeq = 0.0, peqs_switch;
  bool solve_peq = false;
  bool cdft_converged = true, have_hfdens = false, have_dftE = false, do_makeJ = false;
  double au2kcal=ConvFac(HARTREES_TO_KCAL_MOL);
  double au2eV=ConvFac(HARTREES_TO_EV);
  double hfx_lr_coef = rem_read(REM_HFK_LR_COEF) * 0.00000001;

  double eta_A, eta_B; // KCF >> for STEP

 //Prager FDE-ADC
  double E_embed = 0.0;
 //FDE-ADC end

  INTEGER IUnRot=FILE_ROTATION_ANGLES,IUnSSV=FILE_SUBSPACE_VECTORS;
  INTEGER IPseu=FILE_PSEUDOCANNONICAL,IBFGS=FILE_BFGS,IEWSS=FILE_EWSS;
  INTEGER NSSV=0;
  LOGICAL True=1,False=0; /* !!! */

  /* Density Embedding Declarations (BJA) */
  int Frg_Cur;
  // Density Matrix Declarations
  double *jPAfrg2=NULL, *jPAfrg2v=NULL, *jPAfrg12=NULL, *jPAfrg12v=NULL,
    *jPBfrg2=NULL, *jPBfrg2v=NULL, *jPBfrg12= NULL, *jPBfrg12v=NULL;
  // Projection Operator Declarations
  double embed_mu=0.0, mufact=0.0, *jProjOpA=NULL, *jProjOpAv=NULL,
  *jProjOpB= NULL, *jProjOpBv= NULL;

  /* Fractional occupation numbers (DSL) */
  double T = (double) rem_read(REM_FON_T_START); // temperature in K
  const double T_start = T;
  const double T_end = (double) rem_read(REM_FON_T_END); // in K
  const double gap_thresh = 1.0e-4; // threshold for switching FON off
  const int fractional_occupations = rem_read(REM_OCCUPATIONS);
  if (fractional_occupations > 0) {
    printf("\n");
    printf("-------------------------------------------------\n");
    printf("Fractional occupation number algorithm turned on.\n");
    printf("-------------------------------------------------\n");
    printf("\n");
    printf("Initial Temperature = %10.3f K\n", T_start);
    printf("Final Temperature = %10.3f K\n", T_end);
    printf("-------------------------------------------------\n");
    printf("\n");
  }

#ifdef JKN
  qtime_t tdm2d;
  double E_kin, E_pot, vrscr;
  double* TVscr;
  double fake_timer[19];
#endif
  solve_peq = (rem_read(REM_SOLVE_PEQS) == 1) ? true : false;
  if (solve_peq){
     int peqs_expo = rem_read(REM_PEQS_SWITCH);
     double expo=(double)peqs_expo;
     peqs_switch = pow(10.0,-1.0*expo);
     rem_write(0,REM_PEQS_CALLS);
  }
  bool dc_dft = (rem_read(REM_DC_DFT) == 1) ? true : false;
  if (dc_dft) cout << " Enabling density-corrected DFT (DC-DFT)" << endl;

  int dscf_eda = rem_read(REM_DSCF_EDA);
  if (dscf_eda) cout << " Using Hartree-Fock orbitals for SAPT" << endl;

  bool stepjob = rem_read(REM_STEP) > 0 ? true:false;
  bool step_always_alpha = false;
  bool step_always_beta = false;
  if(stepjob)
  {
    printf(" State-targeted energy projection (STEP) procedure active\n");
   // let's also find out which constraint to keep active (if any)
    int step_always_code = rem_read(REM_STEP_ALWAYS_ACTIVE);
    bool unrest = rem_read(REM_JUSTAL) == 1 ? true : false;
    if(step_always_code == step_both)
    {
        step_always_alpha = true;
        step_always_beta  = true;
    }
    else if(step_always_code == step_alpha && unrest)
        step_always_alpha = true;
    else if(step_always_code == step_alpha && !unrest)
    {
        printf("\tSTEP requested to sustain constraint on alpha OR beta\n");
        printf("\torbitals, but orbital type is restricted, sustaining BOTH constraints!\n");
        step_always_alpha = true;
        step_always_beta = true;
    }
    else if(step_always_code == step_beta && unrest)
        step_always_beta = true;
    else if(step_always_code == step_beta && !unrest)
    {
        printf("\tSTEP requested to sustain constraint on alpha OR beta\n");
        printf("\torbitals, but orbital type is restricted, sustaining BOTH constraints!\n");
        step_always_alpha = true;
        step_always_beta = true;
    }
  }

  JustAl = rem_read(REM_JUSTAL);  int Unrestricted=JustAl;
  IPrint = rem_read(REM_SCF_PRINT);
  NAlpha = rem_read(REM_NALPHA);
  NBeta  = rem_read(REM_NBETA);

  NBasis = bSetMgr.crntShlsStats(STAT_NBASIS);
  NBas6D = bSetMgr.crntShlsStats(STAT_NBAS6D);
  NB2    = rem_read(REM_NB2);
  NB2car = rem_read(REM_NB2CAR);
  NOrb   = rem_read(REM_NLINOR);
  MaxSCF = rem_read(REM_MAXSCF);

  int bCodeSec(rem_read(REM_IBASIS));
  BasisSet BasisSec(bCodeSec);
  int NBasSec6D(BasisSec.getNBas6D());
  int bCodeprim(rem_read(REM_BASIS2));
  BasisSet Basisprim(bCodeprim);
  int NBasprim6D(Basisprim.getNBas6D());

  auto sp = libarchive::qchem::qcstorage::get_current_sp();
  auto ef = sp.add_layer<schema::job::sp::energy_function>();
  auto method = ef.add_layer<schema::job::sp::energy_function::method>();
  auto scf = method.add_layer<schema::job::sp::energy_function::method::scf>();
  libarchive::qchem::qcstorage::set_target_energy_function(ef);

  MetSCF = rem_read(REM_METSCF);
  ExtrapFock = (rem_read(REM_EXTRAP_FOCK) == 1) ? 1 : 0;
  if((rem_read(REM_DUAL_BASIS_ENERGY)==1) && rem_read(REM_SMALL_BASIS_LARGE_BASIS)==1)
    ExtrapFock = False; //don't use in large basis set

  if (ExtrapFock==1 || dc_dft || dscf_eda == 1)
    rem_write(0,REM_INCDFT); //screws with extrapolation, probably could be reset at each md step

  // JMH (5/2022) - changed to False, not sure why this was set to true
  if(dscf_eda == 1) rem_write(0,REM_INCFOCK);


  SVPInfo svpinfo;
  INTEGER EFLength=rem_read(REM_EDA_ENERGY_FILE_LENGTH);
  int ISolvent = rem_read(REM_SOLVENT_METHOD);
  LOGICAL usePCM = (ISolvent == PCM) ? 1 : 0;
  //initialize switch and find out of we do a frozen reaction field SCF (PCM variant)
  bool dofRF = false ;
  if(usePCM) dofRF = rem_read(REM_PCM_EQSOLV) ;
  if(usePCM & !dofRF)
  {
     scrf::instance().reset();
     scrf::instance().init(NB2car,NB2);
  }
  LOGICAL useKirkwood = (ISolvent == KIRKWOOD) ? 1 : 0;

  //RST - setup controls for the methods that use fragmentation
  //INTEGER NFragments=rem_read(REM_FRAGMENTS);
  INTEGER LPSCFMI; // NONE-0,GIAN-1,STOLL-2,1F1D-10,1F1D1F-20,1F1D1F1D-11,1F1ARS-15,1F1RS-16
  INTEGER GuessImpr;
  LOGICAL GuessPert,GuessVari;
  INTEGER LPCorr; // NONE-0, ARS-1, RS-5, full SCF-10
  LOGICAL ARStep,RStep;
  LOGICAL LPCorrExact;
  LOGICAL LPNeedsOld;
  LOGICAL ARS_no_scfmi;

  bool hasFracElec = (rem_read(REM_FRACTIONAL_ELECTRON) != 0) ? true : false;

  // JMH (3/2026): formerly REM_OPSING, open-shell singlet spin purification 
  const int rem_opsing = (rem_read(REM_SPIN_PROJ) == NOODLEMAN) ? 1 : 0;

  if (rem_opsing == 1 && rem_read(REM_TRIPLET)==1) 
  { // NAB for correct MOM open-shell singlet states
    FileMan(FM_READ,FILE_ENERGY,FM_DP,1,FILE_POS_SCF_ENERGY,FM_BEG,&ESing);
  }
  if(rem_read(REM_TRIPLET) == 1)
  {
      TripDens();
      NAlpha = NAlpha + 1;
      NBeta  = NBeta - 1;
      rem_write(NAlpha,REM_NALPHA);
      rem_write(NBeta,REM_NBETA);
  }

  Set_Fragment_Variables(&LPSCFMI,&LPCorr,&GuessImpr,
    &GuessPert,&GuessVari,&ARStep,
    &RStep,&LPCorrExact,&LPNeedsOld,&ARS_no_scfmi);

  if (GuessImpr==10 || GuessImpr==15 || GuessImpr==16 ) MaxSCF = 1;
  if (GuessImpr==11 || GuessImpr==20) MaxSCF=2;

  if ( rem_read(REM_SUBSYSTEM)==1 ) {
      FileMan(FM_WRITE,FILE_FRGM_SUBSYSTEM,FM_INT,1,0,FM_BEG,&NBasis);
      FileMan(FM_WRITE,FILE_FRGM_SUBSYSTEM,FM_INT,1,1,FM_BEG,&NOrb);
      FileMan(FM_WRITE,FILE_FRGM_SUBSYSTEM,FM_INT,1,2,FM_BEG,&NAlpha);
      FileMan(FM_WRITE,FILE_FRGM_SUBSYSTEM,FM_INT,1,3,FM_BEG,&NBeta);
      FileMan(FM_WRITE,FILE_FRGM_SUBSYSTEM,FM_INT,1,4,FM_BEG,&NB2);   //KDC
      FileMan(FM_WRITE,FILE_FRGM_SUBSYSTEM,FM_INT,1,5,FM_BEG,&NB2car);//KDC
      FileMan(FM_WRITE,FILE_FRGM_SUBSYSTEM,FM_INT,1,6,FM_BEG,&NBas6D);//KDC
  }
  //endRST

  //DIIS - direct minimization switching info
  IThrDIIS = rem_read(REM_THRESHDIIS); ThrDIIS=TenMin(IThrDIIS);
  NBadDIIS = rem_read(REM_MAXDIIS);
  //RCA - DIIS switching info
  IThrRCA = rem_read(REM_THRESHRCA); ThrRCA=TenMin(IThrRCA);
  NBadRCA = rem_read(REM_MAXRCA);
  // Derivative order in scfman is 0th......
  INTEGER NDeriv = 0;

  /* See if we just want to use the orbitals provided (no SCF) */
  LOGICAL DecompJ;
  DecompJ   = rem_read(REM_DECOMPOSE_ENERGY) > 0;

  /* NoSCF is a misnomer... the Fock matrix gets built and then
     diagonalized once.  MP2Restart=1 means build the Fock matrix but
     don't diagonalize (e.g., to do MP2 with non-HF orbitals). */

  MP2Restart = (rem_read(REM_MP2_RESTART_NO_SCF) > 0) ? 1 : 0;
  NoSCF = MaxSCF <= 0;
  if (NoSCF || MP2Restart) MaxSCF = 1;

  MOMFroz = (rem_read(REM_MOM_FROZEN) > 0) ? 1 : 0;

  /* Decipher the Rem info */

  /* !!! Clean up allocation of DIIS-related arrays for std Roothaan */
  MetDIIS = MetSCF % 10;
  // !!! UseDIIS = MetDIIS > 0 || MetSCF == 0;
  DIISController diisControl(MetDIIS);
  // JKN
  DIISControllerCS DIIScs(MetDIIS); // JKN: alternativ, saves disk space while cyclic sampling...
  LOGICAL CyclicSampling = false;

  if (rem_read(REM_DIIS_SUBSPACE_SIZE) < 0){
#ifdef DEVELOPMENT
    printf(" Using cyclic vector sampling! (class DIISControllerCS)\n\n");
#endif
    CyclicSampling = true;
  }

  //canUseDM = MetSCF >= 10 && MetSCF < 20;
  canUseDM = MetSCF == DM || MetSCF == DIIS_DM;
  usingDM  = canUseDM && MetDIIS == 0;

  //canUseGDM = MetSCF >= 20 && MetSCF < 30;
  canUseGDM = MetSCF == GDM || MetSCF == DIIS_GDM;
  usingGDM  = canUseGDM && MetDIIS == 0;

  //VAR GDIIS - Gradient based DIIS combined with DM
  //canUseGDIIS = MetSCF>=30 && MetSCF < 40;
  canUseGDIIS = MetSCF == PSEUDO;
  usingGDIIS  = canUseGDIIS && MetDIIS == 0;

  //Various forms of Relaxed Constraint Minimization (RCA)
  //   RCA Inherits the DIIS Subspace Size
  //   RCA_DIIS Inherits the Switch Parameters from DIIS_GDM
  UseRCA = MetSCF == RCA || MetSCF == RCA_DIIS;
  NSS = rem_read(REM_DIIS_SUBSPACE_SIZE);
  if(UseRCA){
    jxRCA=QAllocDouble(NSS);
    jARCA=QAllocDouble(NSS*NSS);
    jERCA=QAllocDouble(NSS);
    jE0RCA=QAllocDouble(NSS);
    jdxRCA=QAllocDouble(NSS);
    jgxRCA=QAllocDouble(NSS);
  }

  if(rem_read(REM_EWALD_ON) == 1 && (rem_read(REM_QM_MM_INTERFACE)== JANUS || rem_read(REM_QM_MM_INTERFACE)==ONIOM)){
     jQj = QAllocDouble(NBasis*NBasis*rem_read(REM_NATOMS));
  }

  //NEGF
  // MetSCF is 50 if scf_algorithm = NEGF
  if (MetSCF >= NEGF && MetSCF<= NEGF+4)MetNEGF=MetSCF-NEGF+1;
  //    MetNEGF = MetSCF % NEGF;
  usingNEGF=0;
  if(MetNEGF>0) usingNEGF=1;
  if(usingNEGF==1){
    if(trans_enable==-1) QCrash("You cannot use NEGF with TRANS_ENABLE=-1\n");
    tran_opt = rem_read(REM_TRANS_OPT); //= trans_opt
    trans_get_Vbias(&Vbias, &iVbias,"initial");
  }


  CurDIIS = 0;
  TotDIIS = 0;

  // Allocate and grab the overlap matrix.
  jS = QAllocDouble(NBasis*NBasis);
  GenMatrix S(jS, NBasis, NBasis);
  VRcopy(jS, OneEMtrx().getSm(), NBasis*NBasis);

  if (IPrint >= 2 || rem_read(REM_SCF_FINAL_PRINT) >= 2) {
    S.Print("Overlap Matrix");
    double* jHv = OneEMtrx().getH();
    GenMatrix Hcore(NBasis, NBasis);
    Hcore.ScatterFromSparse(jHv);
    Hcore.Print("Core Hamiltonian");
  }

  Cnverg  = TenMin(KonSCF);

  // RST: NVO init
  double NVOStart = TenMin(rem_read(REM_NVO_START_DIIS));
  INTEGER NVOMethod = rem_read(REM_NVO_METHOD);
  if (NVOMethod > 10 && NVOMethod < 21) { // mixed AO-MO representation
    // Calculate S inverse
    double* jSInv = QAllocDouble(NBasis*NBasis);
    InverseSPD(jS,jSInv,NBasis);
    FileMan(FM_WRITE,FILE_AO_OVERLAP_INV,FM_DP,NBasis*NBasis,0,FM_BEG,jSInv);
    QFree(jSInv);
  }
  // endRST

  N       = NBas6D;
  N2      = N * N;
  //////////////////////////////////////////////////////////////////
  // JMH (01/2008)
  // There are two ways we might add long-range HF exchange:
  // 1) Tony Dutoi's method, using "terf" as switching function.
  //    This is controlled by logical variable add_LRK.
  // 2) More conventional erf switching function of Hirao.
  //    This is controlled by logical variable LRC_DFT.
  // In either case we will need to allocate square matrices.
  //
  // If the terf method is going to be used for real, perhaps (for
  // sanity's sake) we should turn it on using LRC_DFT=2.  This is
  // Just a suggestion, not yet implemented.
  //////////////////////////////////////////////////////////////////
  double omega=0.0,omega2=0.0;
  add_LRK = LRK_init(XCFunc);
  LOGICAL LRC = (rem_read(REM_LRC_DFT) > 0) ? 1 : 0;
  LOGICAL SRC = (rem_read(REM_SRC_DFT) > 0) ? 1 : 0;

  if (SRC){
     //cout << "\n";
     cout << " Short-range corrected functional\n";}
  if (add_LRK)
     cout << " Long-range K will be added via terf\n";
  else if (LRC)
     cout << " Long-range K will be added via erf\n";
  if (add_LRK && LRC)
     QCrash("Cannot do add_LRK and LRC-DFT simultaneously");
  if (SRC)
  {
     omega2 = TenMin(rem_read(REM_OMEGA_NDP))*(double)rem_read(REM_OMEGA2);
     printf(" Coulomb attenuation parameter = %g bohr**(-1)\n",omega2);
     cout << " Short-range K will be added via erfc\n";
  }
  if (add_LRK || LRC){
  // KAUN different omega for different monomer
     if (rem_read(REM_XPOL_OMEGA) == 1){
       int currFrag = xpolCurrFrag();
       int NFrag = rem_read(REM_FRAGMENTS);
       int *w = QAllocINTEGER(NFrag);
       FileMan(FM_READ,FILE_LRC_OMEGAS,FM_INT,NFrag,0,FM_BEG,w);
       rem_write(w[currFrag], REM_OMEGA);
       omega = TenMin(rem_read(REM_OMEGA_NDP))*(double)rem_read(REM_OMEGA);
       printf(" Coulomb attenuation parameter = %g bohr**(-1)\n",omega);
       QFree(w);
     }
     else {
       omega = TenMin(rem_read(REM_OMEGA_NDP))*(double)rem_read(REM_OMEGA);
       printf(" Coulomb attenuation parameter = %g bohr**(-1)\n",omega);
     }
     if (rem_read(REM_OMEGA) == 0)
        QCrash("OMEGA = 0 not allowed in LRC-DFT");
  }
  if (SRC)
  {
     ScaleLR = TenMin(rem_read(REM_OMEGA_NDP))*(double)rem_read(REM_HF_LR);
     ScaleSR = TenMin(rem_read(REM_OMEGA_NDP))*(double)rem_read(REM_HF_SR);
     printf(" C_LR = %g and C_SR = %g \n",ScaleLR,ScaleSR);
     //cout << "\n";
  }

  if (LRC && !XCFunc.IsCoulombAtten() && !SRC && !(rem_read(REM_LEVEXC)==XCFUNC_N12_SX || 
      rem_read(REM_LEVEXC)==XCFUNC_MN12_SX))
  {
     // JMH(04/2008):  Implementation of LRC-DFT has changed since v. 3.2,
     // so it is now consistent with wB97.  (Specifically, each short-range
     // exchange functional has its own name.)  I've added a warning here if
     // it looks like the user might be trying to do things in the old way,
     // or more generally is using LR-HF without SR exchange.
     cout << "\n *************************************************************\n"
          << " **                       Warning:                          **\n"
          << " **  You have requested long-range HF exchange but are not  **\n"
          << " **  using a Coulomb-attenuated (short-range) GGA exchange  **\n"
          << " **  functional.  This is discouraged.  Instead, use a      **\n"
          << " **  short-range exchange functional such as wPBE, muPBE,   **\n"
          << " **  muB88, or Chai and Head-Gordon's LRC hybrid functionals**\n"
          << " **  (wB97, wB97X, wB97X-D, wB97X-2(LP), and wB97X-2(TQZ)). **\n"
          << " **  Consult the Q-Chem documentation regarding LRC-DFT.    **\n"
          << " *************************************************************\n\n";
  }


  /* Get the SCF XC functional */

  //XCFunctional XCFunc(XCFUNC_SCF);


  // DoJ = true, when we have a pure functional with out LRC (long-range corrections)
  DoJ = XCFunc.IsPureDFT() && !(add_LRK || LRC);
  //XCFunc.Print();
  if ((DoJ && dc_dft) || (DoJ && dscf_eda)){
     DoJ = 0;
     do_makeJ = 1;
  }
  ItDM = 0;
  ItRCA = 1;
  NOA  = NAlpha;
  NOB  = NBeta;
  NVA  = NOrb - NOA;
  NVB  = NOrb - NOB;
  INTEGER ISCF = 0;
  if (NOA != NOB || JustAl != 0) ISCF = 1;
  NTheta = NOA*NVA + ISCF*NOB*NVB;
  if (ISCF == 1 && JustAl == 0) {
    ISCF = 2;
    NTheta = NOB*NVA + (NOA-NOB)*(NVA+NOB);
  }
  if(ISCF==2 && UseRCA)
    QCrash("RCA not available for Restricted Open Shell - use GDM!");
  if(ISCF!=0 && rem_read(REM_ROKS)>0)
    QCrash("ROKS excited states keyword is only for singlets with unrestricted = false");

  // Only one unique density for restricted calculations

  if (ISCF == 0)
    NDen = 1;
  else
    NDen = 2;

  /* There is one unique set of MOs for restricted and restricted open-shell
     calculations, but in practice the DM code breaks unless 2 distinct copies
     of the MOs are present for RO.  Therefore we take advantage of the
     opportunity to save space on the MOs only in the restriced case. */

  if (ISCF == 0)  // !!! Could have been if (ISCF != 1)
    NMO = 1;
  else
    NMO = 2;

  LOGICAL do_mrXC = rem_read(REM_DO_MRXC) > 0;
  if (rem_read(REM_EMBED_INTERNAL) > 0 && do_mrXC > 0){
      QCrash("mrXC not supported for density embedding");
  }
  LOGICAL do_FTC = rem_read(REM_FTC) > 0;
  if (rem_read(REM_EMBED_INTERNAL) > 0 && do_FTC > 0){
      QCrash("FTC not supported for density embedding");
  }
  local_interp* interp_grid(0);

  if (do_mrXC) {
    rem_write(0,REM_INCDFT); // mrXC not compatable with incDFT
    //Now setting the xc smooth cs2.
    //Pray that this is the same s2 as in dftman!
    setXCSmoothS2(ShlPrs(bSetMgr.crntCode()).getSigS2());
  }

  /* Print details of the procedure which has been requested */

  PrintSCF(XCFunc,MetSCF,(canUseGDM || canUseDM || canUseGDIIS),NoSCF,Cnverg,MaxSCF,IPrint);
  terseOut(QINK_SCFMAN);

  if (rem_read(REM_GRAIN) > 1) {
    cout << " Using CFMM for Coulomb evaluation." << endl;
    if (IPrint >= 1)
      cout << " CFMM grain = " << rem_read(REM_GRAIN)
	   << "   Multipole order = " << rem_read(REM_CFMM_ORDER) << endl;
  }
  if (rem_read(REM_LIN_K) > 0) {
    cout << " Using LinK for exchange evaluation." << endl;
  }
  if ( rem_read(REM_CHEMSOL) > 0 )
    cout << " Using Langevin Dipoles Model for aqueous solvation." << endl;

  // Are we doing solvent effects via Kirkwood-Onsager?
  //:~: YES!!! Now we have SCF-SCRF code up to arbitrary order of multipole moments
  /*!   Q-Chem implementation (Revised Aug/2007 KST) HF-SCRF with Multipole Expantion  */
  int MulOrd = rem_read(REM_SOLUTE_MULTIPOLE_ORDER);
  int MulOrd1 = MulOrd + 1;
  double* g = NULL;
  double* jFsol  = NULL;
  double* jMMnuc = NULL;
  double* RField = NULL;
  double E_born=0.0, ESolv=0.0;
  if (useKirkwood)
    {
      int i,j,l;
      double Epsilon = rem_read(REM_SOLVENT_DIELECTRIC) / 1.0e4;
      double a0 = rem_read(REM_SOLUTE_RADIUS) / 1.0e4;
      printf(" Kirkwood-Onsager multipolar SCRF: \n"
             " Maximum multipole order     = %d\n"
             " Solvent dielectric constant = %.4f\n"
             " Cavity radius               = %.4f bohr\n",MulOrd,Epsilon,a0);

      // We need some arrays; one time calculation
      int NMMp =  MulOrd1*MulOrd1;
      jMMnuc = QAllocDouble(NMMp);
      RField = QAllocDouble(NMMp);
      FileMan(FM_READ,FILE_NUC_MULT_MATRIX,FM_DP,NMMp,0,FM_BEG,jMMnuc);
      if(!rem_read(REM_SCF_UPDATE_RXN_FIELD))
	{
	  cout<< "Read Reaction Field from Disk ...\n";
	  FileMan(FM_READ,FILE_SOL_RXN_FIELD,1,NMMp,0,FM_BEG,RField);
	}

      g = QAllocDouble(MulOrd1);
      for(l=0;l<=MulOrd;l++)
	{
	  // pow(a0,(2*l+1.0)) replaces
	  double tempBuff=1.0;
	  for(i=0;i<(2*l+1);i++)
	    tempBuff *= a0;

	  g[l] = (l + 1.0) * (Epsilon - 1.0) / ( (l + ( l + 1.0) * Epsilon ) * tempBuff );
	}

      // We need Born Term if the molecule has net charge
      int Charge = rem_read(REM_MICHARGE);
      if(Charge!=0)
	{
	  E_born = -0.5*g[0]*Charge*Charge;
	  printf(" Born term (E_born)          = %.8f a.u.",E_born);
          printf(" = %.4f kcal/mol\n",E_born*au2kcal);
	}

      if (IPrint >= 2)
      	{
	  cout.precision(10); // **
	  for(l=0;l<=MulOrd;l++)
	    cout << "g["<<l<<"] = "<<g[l]<<endl;
	  cout <<endl;

	  for(i=0;i<NMMp;i++)
	    cout <<"\t"<<jMMnuc[i];
	  cout <<endl;
	  cout <<endl;

	  SetDefaultFPFormat(cout); //**
	}
    } // close if(useKirkwood)


  bool do_efp = EFP2::instance().initialized();

  if (do_efp)
	EFP2::instance().reorient_geometry();

  double E_EFP = 0.0;
  /* Set up some pointers */


  //AJWT SCF_SAVEMINIMA  - how many SCF minima do we save
  // JMH (11/2021): really we shouldn't instantiate this object if we're not doing metadynamics...
  SCFMinFind mf(ItDM,diisControl,IPrint);

  /* !!! Make allocation efficient for DM !!! */
  if ((XCFunc.HasHF() || add_LRK || LRC || mf.iSaveMinima) || (dc_dft && XCFunc.IsPureDFT()) || 
      (dscf_eda && XCFunc.IsPureDFT())
     ) 
  {
    jPA = QAllocDouble(N2*NDen);
    jPB = jPA + N2*(NDen-1);
  }
  else
    jKA = jKB = NULL;


  jFAv = QAllocDouble(NB2car*NDen);
  jFBv = jFAv + NB2car*(NDen-1);

  jPAv  = QAllocDoubleWithInit(NB2car*NDen);
  jPBv  = jPAv + NB2car*(NDen-1);
  jXCAv = QAllocDouble2(NB2car*NDen,shared);
  jXCBv = jXCAv + NB2car*(NDen-1);
  VRload(jXCAv,NB2car*NDen,0.0);
  //jJv   = QAllocDoubleWithInit(NB2car*NDen);
  // Overlay alpha XC vector and J vector
  jJv   = jXCAv;
  if (dc_dft || dscf_eda) jJv_temp = QAllocDouble(NB2car*NDen);
  if (canUseGDM || canUseDM) {
    /* could be more efficient for restricted */
    jTh = qalloc_double(NOA*NVA+NOB*NVB);
    jGr = qalloc_double(NOA*NVA+NOB*NVB);
  } else if (canUseGDIIS) {
    if (rem_read(REM_ISYM_RQ) > 0) {QCrash(" Turn symmetry off for GDIIS covergence !");}
    Curv=1.0;
    Step=1.0;
    //If not SAD guess, first step should be small
    if(ISCF != 1) {NTheta=NOrb*NBasis;} else {NTheta=2*NOrb*NBasis;}
    jGr = qalloc_double(NTheta);
  }

  /* Read in a density from disk.  Might use the sparse form. */
  bool use_Pv = XCFunc.IsPureDFT() && !(add_LRK || LRC) && !dc_dft && !dscf_eda;
  scfman_read_guess_density(use_Pv, NDen, jPAv, jPBv, jPA, jPB);

  //BJA_guess
  double* jPAoriginal;
  if (rem_read(REM_EMBED_INTERNAL)) {
    jPAoriginal = QAllocDoubleWithInit(N*N*NDen);
    jPA = QAllocDoubleWithInit(N*N*NDen);
#ifdef DEVELOPMENT
	FileMan(FM_READ,FILE_DENSITY_MATRIX,FM_DP,N2*NDen,0,FM_BEG,jPA);
    if (IPrint >= 2) {
      MatPrint(jPA, NBasis, NBasis, "jPA From SAD Guess");
    }
#endif
    FileMan(FM_READ,FILE_FRAG_DENS,FM_DP,NBasis*NBasis,NBasis*NBasis + NBasis*NBasis,FM_BEG,jPA);
    FileMan(FM_WRITE,FILE_DENSITY_MATRIX,FM_DP,N2,0,FM_BEG,jPA);
    if (IPrint >= 2) {
      MatPrint(jPA, NBasis, NBasis, "jPA From Supermolecular SCF");
    }
    ScaV2M(jPA,jPAv,True,False);
    VRcopy(jPAoriginal, jPA, N2*NDen);
  }

  double ENuclear; //Nuclear Repulsion energy
  FileMan(FM_READ,FILE_ENERGY,FM_DP,1,FILE_POS_NUC_REPUL_ENERGY,FM_BEG,&ENuclear);

  //// BJA_nuc
  if (rem_read(REM_EMBED_INTERNAL)) {
    int NFrgm = rem_read(REM_FRAGMENTS);
    double * ENuc = QAllocDoubleWithInit(NFrgm+2);
    FileMan(FM_READ,FILE_ENUCS,FM_DP,NFrgm+2,0,FM_BEG,ENuc);
    Frg_Cur = int(ENuc[NFrgm+1]);
#ifdef DEVELOPMENT
    cout << "ENuc[" << Frg_Cur << "] = " << ENuc[0] << endl;
    cout << "ENuc[NFrgm] = " << ENuc[NFrgm] << endl;
#endif
    ENuclear = ENuc[Frg_Cur] + (ENuc[NFrgm] / 2.0);
    //cout << "ENuclear read in from FILE_ENERGY: " << ENuclear  << endl;
  }

  double *jCAXC=NULL;
//#ifdef DEVELOPMENT
  if (rem_read(REM_DOMOS_DFT) > 0 || XCFunc.HasTau() || rem_read(REM_ROKS)>0) {
    if (rem_read(REM_ROKS)>0)
      jCAXC = QAllocDouble(NBas6D*NOrb*NMO);
    else
      jCAXC = QAllocDouble(NBasis*NOrb*NMO);
    /* !!! Load up the MO coeffs for use by DFTman */
    FileMan(FM_READ,FILE_MO_COEFS,FM_DP,NBasis*NOrb*NMO,0,FM_BEG,jCAXC);
    //    FileMan(FM_READ,FILE_MO_COEFS,FM_DP,NBasis*NOrb,0,FM_CUR,jCB);
    if(LPSCFMI > 0) {
       OrthogonalizeMOs(jCAXC, N, NOA);   //YMao: orthogonalize occ ALMOs and feed them into DFTMan (feeding non-ortho MOs is invalid)
       if (NMO > 1) {OrthogonalizeMOs(jCAXC+N*NOrb, N, NOB);}
    }
  }
//#endif

  /* !!! ROHF is done just a little bit differently !!! Fix in gesman */

  if (ISCF == 2 && !(usingDM || usingGDM || usingGDIIS))
    QCrash("Restricted open-shell calculations must use Direct Minimization"
           " or Geometric Direct Minimization (default)");

  /* Now that the allocation is over, we'll work only with pure
     functions from here on */

  N  = NBasis;
  N2 = N * N;

  /* Do we plan to use the Integrals Storage Manager for this SCF? */

  LOGICAL UseISM = CanUseIntsStorageSCF();

  t0 = QTimerOn();  /* Time the SCF */


  // Declaration Needed for IncFock....
  double *jdPv=NULL,  *jdJv=NULL,  *jPvlast=NULL,  *jJvlast=NULL;
  double *jdPA=NULL,  *jdPB=NULL,  *jPAlast=NULL,  *jPBlast=NULL;
  double *jdKA=NULL,  *jdKB=NULL,  *jKAlast=NULL,  *jKBlast=NULL;
  double *jdKAsr=NULL,*jdKBsr=NULL,*jKAsrLast=NULL,*jKBsrLast=NULL;
  LOGICAL Matrix2E = ((DoJ || XCFunc.HasHF() || add_LRK || LRC) || (dc_dft && XCFunc.IsPureDFT()) || (dscf_eda && XCFunc.IsPureDFT())) ? 1 : 0;
  SCFConvControl  SCFConv(UseISM);

  // Some stuff for Chipman's SVP
  LOGICAL SVP_Conv;
  double  SVP_Error;
  if(SCFConv.UseSVP()){
    SVP_Conv = 0;
    if(rem_read(REM_SVP_PATH)==1){
      printf(" Skip gas-phase calculation and proceed directly to SS(V)PE\n");
      SCFConv.SwitchOnSVP();
    }else{
      printf(" Gas-phase calculation in preparation for subsequent SS(V)PE\n");
      SCFConv.SwitchOffSVP();
    }
  }
// AJWT metadynamics
   mf.Init();           // Setup minfinding data etc.
   mf.InitOrbitals(jPA,jPB,jPAv,jPBv);   // Initialize orbitals and density if we are reading in minima to converge to
// /AJWT metadynamics
  /* Begin the iterations */

  ETot=0.0; DEMax=1e10;
  LOGICAL IncDFTDIISReset = False;
  InterLangString Comment;
  rem_write(0,REM_SCF_CONVERGED);
  LOGICAL Converged = FALSE;

  // CDS add empirical dispersion if requested
  // Add our contribution to ETot
  INTEGER PLUSD = rem_read(REM_EMPIRICAL_DISPERSION);
  if (PLUSD) {
    Edisp = empirical_dispersion();
  }
  else Edisp = 0.0;

// SEM add airbed energy if requested
// correction to be added to Etot
   INTEGER PLUSAIR = rem_read(REM_AIRBED);
   if (PLUSAIR) {
      Eairbed = airbed();
   }
   else Eairbed = 0.0;


/* TAV: If We're doing QM/MM, allow it to skip the SCF, if desired */
   LOGICAL QMMM=rem_read(REM_QM_MM);
   if(NoSCF && QMMM) {
     Converged=TRUE;
     rem_write(1,REM_SCF_CONVERGED);

     //@@TAV - need to write out some things...
     jFA = QAllocDouble(N2*NDen);
     jFB = jFA + (NDen - 1) * N2;
     FileMan_Open_Write(FILE_TEMP_FOCK);
     FileMan(FM_WRITE,FILE_TEMP_FOCK,FM_DP,N*N,0,FM_BEG,jFA);
     FileMan(FM_WRITE,FILE_TEMP_FOCK,FM_DP,N*N,0,FM_CUR,jFB);
     FileMan_Close(FILE_TEMP_FOCK);

     FileMan_Open_Read(FILE_SPARSE_DENSITY_MATRIX);
     FileMan(FM_READ,FILE_SPARSE_DENSITY_MATRIX,FM_DP,NB2,0,FM_BEG,jPAv);
     if (NDen == 2)
        FileMan(FM_READ,FILE_SPARSE_DENSITY_MATRIX,FM_DP,NB2,0,FM_CUR,jPBv);
     FileMan_Close(FILE_SPARSE_DENSITY_MATRIX);

     ScaV2M(jFA,jPAv,True,True);
     if (NDen == 2) ScaV2M(jFB,jPBv,True,True);
     FileMan(FM_WRITE,FILE_DENSITY_MATRIX,FM_DP,N2,0,FM_BEG,jFA);
     FileMan(FM_WRITE,FILE_DENSITY_MATRIX,FM_DP,N2,0,FM_CUR,jFB);

     QFree(jFA);
   }
   /* End QM-MM Exception*/

  double *jC0,*jFC,*jPC; // TDK Adjustments for ROKS
  if (rem_read(REM_ROKS) > 0) {
    jC0 = QAllocDouble(NBas6D*NOrb);
    roks_singly_occupieds(roks_a,roks_b);
    if (XCFunc.IsPureDFT()) { // Need square P for ROKS even if XCFunc is pure DFT
      jPA = QAllocDouble(N2);
      jPB = jPA;
    }
  }

  //RST: time scf
  qtime_t rusty10;
  double rusty11[3];
  rusty10 = QTimerOn();

  INTEGER cosmo = rem_read(REM_SOLVENT_METHOD) == COSMO;
  double *jHv_cosmo = NULL;
  double Ediel=0.0;
  if (cosmo) {
    scrf::instance().reset();
    scrf::instance().init(NB2car,NB2);
    /*
     jHv_cosmo = QAllocDouble(NB2car);
     INTEGER One = 1;
     qchem_cosmo(&One, jHv_cosmo, &Ediel, jPAv);
     */
  }


  if(usingNEGF) {
    // read restart density matrix for NEGF
    tran_restart = rem_read(REM_TRANS_RESTART);
    if(tran_restart==1 & iVbias<=1) {
       read_restart_NEGF_files(NBasis,NMO,jPA,jPB,jFA,jFB,jS);
	          FileMan(FM_WRITE,FILE_DENSITY_MATRIX,1,N2,0,1,jPA);
       if(NMO==2) FileMan(FM_WRITE,FILE_DENSITY_MATRIX,1,N2,0,2,jPB);
    }
  }

  // BJA_INIT: Initialize Density Embedding:
  if(rem_read(REM_EMBED_INTERNAL)) {
     /*
     *  Search Keyword for changes made throughout scfman.C:
     *      BJAc =      General comments
     *      BJA_INIT =  Allocations and initialization of embedman within scfman
     *      BJA_H =     Read in 1-e matrix from dimer calc
     *      BJA_J =     MakeJ[jPAv] -> MakeJ[jPAfrg12v]
     *      BJA_XC =    DFTman[jPAv] -> DFTman[jPAfrg12v]
     *      BJA_Corr =  Add mu*Tr(jPA*jPAfrg2) correction to ETot
     *      BJA_FOCK =  F = h1 + J1 - XC1 + J12 - XC12
     *      BJA_P =     Generating Pfrg12
     *      BJA_FIX =   Fix Fock Matrices and resymmetrize before writing
     *      BJA_JKN =   Custom Energy Component Outputs
     *
    */
    cout << "\n-----------------------------------------------------------------------------------------" << endl;
    cout << "         ============== Density Embedding SCF For Fragment " << Frg_Cur+1 << "  ==============         " << endl;
    cout << "-----------------------------------------------------------------------------------------" << endl;
    // Density Vars
    jPAfrg2 = QAllocDoubleWithInit(N2);
    jPAfrg2v = QAllocDoubleWithInit(NB2car);
    jPAfrg12 = QAllocDoubleWithInit(N2);
    jPAfrg12v = QAllocDoubleWithInit(NB2car*NDen);
    // Projection Operator Vars
    jProjOpA = QAllocDoubleWithInit(N2);
    jProjOpAv = QAllocDoubleWithInit(NB2car);
    embed_mu = rem_read(REM_EMBED_MU);
    mufact = pow(10.0,embed_mu);
    if (NDen == 2) {
      jProjOpB = QAllocDoubleWithInit(N2);
      jProjOpBv = QAllocDoubleWithInit(NB2car);
      jPBfrg2 = QAllocDoubleWithInit(N2);
      jPBfrg2v = QAllocDoubleWithInit(NB2car);
      jPBfrg12 = QAllocDoubleWithInit(N2);
      jPBfrg12v = QAllocDoubleWithInit(NB2car);
    }
    if (IPrint >= 1){
      cout << "mu = 10^" << embed_mu << endl;
      cout << "NDen: " << NDen << endl;
      cout << "NMO: " << NMO << endl;
      cout << "NBasis: " << NBasis << endl;
      cout << "NOrb: " << NOrb << endl;
      cout << "N: " << N << endl;
      cout << "NB2car: " << NB2car << endl;
      cout << "NB2: " << NB2 << endl;
    }
    // Read in density of system B
    FileMan(FM_READ,FILE_FRAG_DENS,FM_DP,NBasis*NBasis,NBasis*NBasis*NDen,FM_BEG,jPAfrg2);
    FileMan(FM_READ,FILE_FRAG_DENS,FM_DP,NBasis*NBasis,0,                 FM_BEG,jProjOpA); //1100
    ScaV2M(jPAfrg2,jPAfrg2v,True,False); //jPAfrg2 -> jPAfrg2v
    if (NDen == 2)
    {
        FileMan(FM_READ,FILE_FRAG_DENS,FM_DP,NBasis*NBasis,NBasis*NBasis*NDen+NBasis*NBasis,FM_BEG,jPBfrg2);
        FileMan(FM_READ,FILE_FRAG_DENS,FM_DP,NBasis*NBasis,NBasis*NBasis,                   FM_BEG,jProjOpB); //1100
        ScaV2M(jPAfrg2,jPAfrg2v,True,False); //jPAfrg2 -> jPAfrg2v
    }
#ifdef DEVELOPMENT
    if (IPrint >= 2){
      MatPrint(jPAfrg2, NBasis, NBasis, "jPAfrg2");
      MatPrint(jS, NBasis, NBasis, "jS");
      MatPrint(jProjOpA, NBasis, NBasis, "jProjOpA Alpha");
      if (NDen == 2) {
        //MatPrint(jPB, NBasis, NBasis, "jPfrg1 (jPB) Beta");
        MatPrint(jPBfrg2, NBasis, NBasis, "jPBfrg2");
        MatPrint(jProjOpA+N2, NBasis, NBasis, "jProjOpA Beta");
      }
    }
#endif
   if (IPrint >= 2) {
     MatPrint(jPA, N, N, "jPA From Supermolecular SCF");
   }
 }

 // Begin SCF Cycles
  for (IteSCF = 1, EMax = 1e10; IteSCF <= MaxSCF && !Converged; ++IteSCF) {
    rem_write(IteSCF,REM_ITESCF);
    if (MaxSCF == 1 && rem_read(REM_IGUESS) == READ)
       rem_write(IteSCF+1, REM_ITESCF);
    Comment = "";
    if (IteSCF == 1 && rem_read(REM_IDEMPOTENT_GUESS) == 0)
      {ConvOK = FALSE;} else {ConvOK = TRUE;}
    tdE = QTimerOn();
    if(SCFConv.doingSVP()){
      if(IteSCF==1){
	//PrintQAllocStats();
	hondostart(&svpinfo.MemoryDW);
	if(rem_read(REM_SVP_READPUNCH)==1){
	  printf("\n The SVP solvation code will read ");
          printf("the initial charges from the scratch directory\n");
	  svpPunchMove();
	  rem_write(1,REM_SVP_READINPUT);
	}
	INTEGER method=0;
	svp_begin(&method);
	svpinfo.Method = method;
      }
    }
    //BJAc: Throw error when hybrid functional called
    if ( XCFunc.HasHF() && rem_read(REM_EMBED_INTERNAL) ) {
      QCrash( "Embedding not supported with HF-Exchange \n" );
    }
    if (( XCFunc.HasHF() || add_LRK || LRC ) || (dc_dft && XCFunc.IsPureDFT() && !have_hfdens) || 
        (dscf_eda && XCFunc.IsPureDFT() && !have_hfdens)
       ) 
    {

#if 0
#ifdef DEVELOPMENT

      // !!! Check symmetry of density, to catch cases where symmetry is
      // !!! broken and hence the application of symmetry would fail

      if (rem_read(REM_ISYM_RQ) > 0) {
	INTEGER NOpUse = rem_read(REM_NOP_USE);
	if (NOpUse > 1) {
	  printf("Checking symmetry of density matrix...\n");
	  double* Pbak = QAllocDouble(N2);

	  // Alpha

	  VRcopy(Pbak,jPA,N2);
	  P2SymM(jPA,0,0);
	  //MatPrint(Pbak,N,N,"Orig PA");
	  double RNop = 1.0 / NOpUse;
	  VRscale(jPA,N2,RNop);
	  //MatPrint(jPA,N,N,"Symm PA");

	  double DMax = 0.0;
	  for (int ii = 0; ii < N2; ++ii)
	    DMax = max(fabs(jPA[ii]-Pbak[ii]),DMax);
	  if (DMax > 1.0e-7)
	    printf("Warning:  Max alpha deviation from symmetry = %E\n"
		   "Alpha density failed symmetry check\n",DMax);
	  //		 "using symmetrized density\n"
	  VRcopy(jPA,Pbak,N2);  // Don't use symmetrized density yet

	  // Beta

	  if (NDen == 2) {
	    VRcopy(Pbak,jPB,N2);
	    P2SymM(jPB,0,0);
	    //MatPrint(Pbak,N,N,"Orig PB");
	    double RNop = 1.0 / NOpUse;
	    VRscale(jPB,N2,RNop);
	    //MatPrint(jPB,N,N,"Symm PB");

	    DMax = 0.0;
	    for (int ii = 0; ii < N2; ++ii)
	      DMax = max(fabs(jPB[ii]-Pbak[ii]),DMax);
	    if (DMax > 1.0e-7)
	      printf("Warning:  Max beta deviation from symmetry = %E\n"
		     "Beta density failed symmetry check\n",DMax);
	    //		   "using symmetrized density\n"
	    VRcopy(jPB,Pbak,N2);  // Don't use symmetrized density yet
	  }
	  QFree(Pbak);
	}
      }
#endif
#endif
      // Need to create sparse versions of P
      ScaV2M(jPA,jPAv,True,False);
      if (NDen == 2) ScaV2M(jPB,jPBv,True,False);
    }

    // dual basis
    double* jPold=NULL, *jFold=NULL;
    // RST: use dual-basis code to perform LP correction.
    if ( (rem_read(REM_SMALL_BASIS_LARGE_BASIS) == 1 && rem_read(REM_DUAL_BASIS_ENERGY) ==1)
        || LPNeedsOld ) {
    //endRST
      jPold = QAllocDouble(N2*NDen);
      if ((XCFunc.HasHF() || add_LRK || LRC) || (dc_dft && XCFunc.IsPureDFT() && !have_hfdens) || 
          (dscf_eda && XCFunc.IsPureDFT() && !have_hfdens)
         ) 
      {
	VRcopy(jPold,jPA,NBasis*NBasis);
	if (NDen == 2) VRcopy(jPold+N2,jPB,NBasis*NBasis);
      }
      else {
	ScaV2M(jPold,jPAv,True,True);
	if (NDen == 2) ScaV2M(jPold+N2,jPBv,True,True);
      }
      if (rem_read(REM_USE_LS_SCREENING) == 1)
        shell_labelling(jPold);
    }

     // BJA_P!
    /* For the calculation of the one-electron energy and the J matrix
       and energy, we need the total density.  Construct the total density
       matrix in jPAv. */

    if (NDen == 2) {
      VRadd(jPAv,jPAv,jPBv,NB2);
      if (rem_read(REM_EMBED_INTERNAL)) {
        VRadd(jPAfrg2v, jPAfrg2v, jPBfrg2v ,NB2car);
        VRadd(jPAfrg12v, jPAv, jPAfrg2v ,NB2car);
        ScaV2M(jPAfrg12,jPAfrg12v,True,True);
        if (IPrint >= 2){
          MatPrint(jPAfrg12, N*NDen, N*NDen, "Full jPAfrg12");
          //MatPrint(jPAfrg12v,NB2car, 1, "Full jPAfrg12v");
          MatPrint(jPAfrg2, N*NDen, N*NDen, 1, "Full jPAfrg2");
          //MatPrint(jPAfrg2v, NB2car, 1, "Full jPAfrg2v");
        }
      }
    }
    else {
      VRscale(jPAv,NB2, 2.0);
      if (rem_read(REM_EMBED_INTERNAL)) {
        VRscale(jPAfrg2v,NB2, 2.0);
        VRadd(jPAfrg12v,jPAv,jPAfrg2v,NB2);
        ScaV2M(jPAfrg12,jPAfrg12v,True,True);
        if (IPrint >= 2){
          MatPrint(jPAfrg12, N*NDen,N*NDen, "Full jPAfrg12");
          //MatPrint(jPAfrg12v,NB2car, 1, "Full jPAfrg12v");
          MatPrint(jPAfrg2, N*NDen, N*NDen, "Full jPAfrg2");
          //MatPrint(jPAfrg2v, NB2car, 1, "Full jPAfrg2v");
        }
      }
    }



    double SVPEnergy=0.0;
    if(SCFConv.doingSVP()){
      INTEGER IUPRXN,IQORP;
      LOGICAL SCF_Conv = 0;
      INTEGER SVPmem = svpinfo.MemoryDW;
      svpman(jPAv,&IteSCF,&SCF_Conv,&IUPRXN,&IQORP,&SVPEnergy,
             &SVP_Conv,&SVP_Error,&SVPmem,svpinfo.TmpValuesArray);

      if(IQORP==0){
	SetExternalCharges();
      }
    }

    //printf("EMax = %f, peqs_switch = %f\n",EMax,peqs_switch);
    if (solve_peq && EMax < peqs_switch)
      Epeq = PEQS_Main(jPAv);

    if (usePCM & dofRF)
    {
      ////////////////////////////////////////////////////////////////////////
      // E_PCM is the vector of solvation free energies                     //
      // (0) = G_es, electrostatic interaction of solute with solvent       //
      // (1) = G_cav, cavitation                                            //
      // (2) = G_dis, dispersion                                            //
      // (3) = G_rep, repulsion                                             //
      // (4) = q-nuke interaction (with non-eq SS corrections)              //
      // (5) = q-ESPMM interaction for QM/MM/PCM with JANUS interface       //
      // (6) = Extra space for debugging                                    //
      // (7-14) = DEFESR energies (parameterized and unparameterized)
      ////////////////////////////////////////////////////////////////////////
      if(jE_PCM == NULL) jE_PCM = QAllocDouble(15);
      VRload(jE_PCM,15,0.0);

      //here we check if we want to follow fRF approach i.e. SCF in the RF of another state
      int pcm_success = 0 ;
      if(dofRF){ // this switches on fRF SCF by calling the specific PCMman Jobtype
         rem_write(0,REM_PCM_FINAL);
         pcm_success = PCMman(PCMJOB_EQ_SS_FRF, jPAv, jE_PCM);
      }else{ //normal RSCF calculation using PCMman
         // Modify a rem variable to let PCMman know we are NOT on the final PCM call
         rem_write(0,REM_PCM_FINAL);
	 pcm_success = PCMman(PCMJOB_ENERGY, jPAv, jE_PCM);
      }
      #ifdef DEVELOPMENT
      if(rem_read(REM_PCM_PRINT) > 1)
        cout << "PCM Status: " << pcm_success << endl;
      if(rem_read(REM_PCM_PRINT) > 0){
        cout << "Current PCM G_elec  = "
             << jE_PCM[0]*0.5 << " hartree";
        cout << " = " << jE_PCM[0]*au2kcal
             << " kcal/mol" << endl;
      }
      #endif

      // -- Old buggy shell pair method -- //
      /*
      int ITessMeth = rem_read(REM_PCM_TESSEL_METHOD);
      if (ITessMeth == SWIG || ITessMeth == ISMOOTH){
        // If doing smooth PCM with a QM region,
        // remake shell pairs for smooth pcm here before we redo the STV
        reMakeAll();
        int bCode = rem_read(REM_BASIS2);
        BasisSet pcm_s1(bCode);
        ShlPrs pcm_s2(pcm_s1);
      }
      */
      // -- New method -- // --> Don't remake the shell pairs!

    }else if(usePCM)
      scrf::instance().compute(jPAv);

    // Compute EFP wavefunction dependent energy component (polarization)
    // Also keep track of whether need to update multipole and polarization intergrals
    if (do_efp) {
        E_EFP = EFP2::instance().get_wf_dependent_energy(jPAv, NB2car * NDen);
        if (IteSCF == 1) {
            EFP2::instance().update_multipole_field(true);
            EFP2::instance().update_pol_field();
        }
    }

    // BJA_H!
    // Get the one-electron Hamiltonian
    double* jHv = OneEMtrx().getH();

////KAUN add the interaction between electron and electron density for MBE
   if(rem_read(REM_MANY_BODY_INT) == 1 &&
      rem_read(REM_MBE_EMBED) == mbe_embed_Q)
   {
      double *jIv = QAllocDouble(NB2);
      FileMan(FM_READ,FILE_XPOL_EPC_INTERACTION_MATRIX,FM_DP,NB2,0,FM_BEG,jIv);
      VRadd(jHv,jIv,NB2);
      QFree(jIv);
   }
////KAUN

////KAUN, for FMO
   if(rem_read(REM_FRAG_MOL_ORB) == 1 &&
      rem_read(REM_XPOL_EMBED) == xpol_embed_DENS && !isXPol
     )
   {
      double *jIv = QAllocDouble(NB2);
      FileMan(FM_READ,FILE_XPOL_EPC_INTERACTION_MATRIX,FM_DP,NB2,0,FM_BEG,jIv);
      VRadd(jHv,jIv,NB2);
      VMtrace(&fmoElecDen,jPAv,jIv,True);
      QFree(jIv);
   }
////KAUN

    if(rem_read(REM_CDFTCI_FRAGMENT)) {
	cdftci_block_wipe_h(jHv,NBasis,N);
    }
    // LDJ - update electrostatic interaction prior to getting one E energy
    if(isXPol)
    {
       INTEGER currFrag = xpolCurrFrag();
       double *jXPOLv = QAllocDouble(NB2);
       FileMan(FM_READ,FILE_XPOL_ES_INTERACTION_MATRIX,FM_DP,NB2,0,FM_BEG,jXPOLv);
       FileMan(FM_READ,FILE_XPOL_ENERGY,FM_DP,1,9*currFrag+8,FM_BEG,&xpNucMull);
       VRadd(jHv,jXPOLv,NB2);
       VMtrace(&xpElecMull,jPAv,jXPOLv,True);
       QFree(jXPOLv);

       if(rem_read(REM_XPOL_MM_PC) > 0){ //KAUN XPol QMMM
         double *jIqv = QAllocDouble(NB2);
         FileMan(FM_READ,FILE_XPOL_MM_ES_MATRIX,FM_DP,NB2,0,FM_BEG,jIqv);
         FileMan(FM_READ,FILE_XPOL_MM_NUC,FM_DP,1,0,FM_BEG,&xpNucExt);
         VRadd(jHv,jIqv,NB2);
         VMtrace(&xpElecExt,jPAv,jIqv,True);
         QFree(jIqv);
       }
    }


    /* Knock out the one-electron energy */
    VMtrace(&E1,jPAv,jHv,True);

    // LDJ - update one E matrix for terms required for min
    if(isXPol)
    {
       double *jXPOLv = QAllocDouble(NB2);
       FileMan(FM_READ,FILE_XPOL_MIN_INTERACTION_MATRIX,FM_DP,NB2,0,FM_BEG,jXPOLv);
       VRadd(jHv,jXPOLv,NB2);
       VMtrace(&xpMinE,jPAv,jXPOLv,True);
       QFree(jXPOLv);
    }

//KAUN
   if(rem_read(REM_FRAG_MOL_ORB) == 1 &&
      rem_read(REM_XPOL_EMBED) == xpol_embed_DENS && !isXPol
     )
   {
      double *jIv = QAllocDouble(NB2);
      FileMan(FM_READ,FILE_XPOL_EPC_MIN_INTERACTION_MATRIX,FM_DP,NB2,0,FM_BEG,jIv);
      VRadd(jHv,jIv,NB2);
      VMtrace(&fmoMinE,jPAv,jIv,True);
      FileMan(FM_WRITE,FILE_FMO_MINE_INTERACTION_MATRIX,FM_DP,1,0,FM_BEG,&fmoMinE);
      QFree(jIv);
   }
//KAUN

    // if we are doing cosmo, need
    if (cosmo) {
       scrf::instance().compute(jPAv);
       Ediel = scrf::instance().energy();
       scrf::instance().getH(&jHv_cosmo,NULL);
      /*
       INTEGER Two = 2;
       qchem_cosmo(&Two ,jHv_cosmo, &Ediel, jPAv);
       //MatPrint(jHv_cosmo, 1, NB2, "jHv_cosmo");
       printf("Ediel: %12.7f\n", Ediel);
       */
       VRadd(jHv, jHv, jHv_cosmo, NB2);
       E1 += Ediel;
    }

#ifdef JKN
    double* TVscr = OneEMtrx().getT();
    VMtrace(&E_kin,jPAv,TVscr,True);
    TVscr = OneEMtrx().getV();
    VMtrace(&E_pot,jPAv,TVscr,True);
    TVscr = NULL;
#endif

    /* Correct the energy for solvation */
    if(SCFConv.doingSVP()){
      // Chipman's SS(V)PE code, using iso-density cavity
      E1 += SVPEnergy;
    }else if(usePCM & dofRF){
      // AWL --  general PCM code, using cavity based on atomic spheres

      //  Add the surface charge -- solute nuclei electrostatic interation energy.
      //  ~JMM: we do the same for fRF-SCF, since we have used frozen reation field to get jE_PCM[4]
      // cout << "### Adding nuclear-RF interaction of " << jE_PCM[4]*27.2114 << " eV" << endl ;
      //  (and non-eq SS corrections if doing non-eq PCM job)
      E1 += jE_PCM[4];

      //Write nuclei-ASC interaction to disk for later use in PTD/PTED approach
//      FileMan(FM_WRITE,FILE_ES_RF_INTERACTION,FM_DP,1,101,FM_BEG,&jE_PCM[4]);

      if(!dofRF){ // for standard GS equilibrated PCM: ~JMM
         //  The surface charge -- solute electrostatic interaction energy is exactly
         //  twice the work of inducing those surface charges. Thus, we subtract off half
         //  of the electrostatic energy to form the free energy in solution.
         //  Note that the surface charge -- solute electrons electrostatic interaction energy
         //  is already part of E1 here via the added external charges.
         E1 += -0.5*jE_PCM[0];

      }else if(dofRF){//for frozen reaction field PCM ~JMM
         // In case of fRF-SCF, the polarization energy that has to be subtracted is not just
         // half of the interaction energy of the ground state with the RF, but half of the interaction
         // of the respective, equilibrated excited state with its self induced RF.
         // This value has been calculated and stored to disk in the previous iteration.
         // Here we read it and add it to the SCF energy.
         int state_number = rem_read(REM_PCM_EQSTATE) ;//which state are we equilibrating?
         double ES_RF_interaction = 0.0 ;
         FileMan(FM_READ,FILE_ES_RF_INTERACTION,FM_DP,1,state_number,FM_BEG,&ES_RF_interaction);
         E1 += -0.5*ES_RF_interaction;

         //cout << "### Standard polarization = " << 0.5*jE_PCM[0]*27.2114 << " eV" << endl ;
         //cout << "###  fRF-PCM polarization = " << 0.5*ES_RF_interaction*27.2114 << " eV (for state# " << state_number << ")" << endl ;
      }

      //  Lastly, we also add in half of the surface charge -- MM atomic charge interaction
      //  energy, which is non-zero only if doing QM/MM/PCM with JANUS interface
      if (rem_read(REM_QM_MM_INTERFACE) == 2)
        E1 += 0.5*jE_PCM[5];
    }else if(usePCM){
      //printf("E1 before correction equals %4.8f\n", E1);
      //double Eold = E1;
      double E_pcm = scrf::instance().energy();
      E1 += E_pcm;
    }

    if(solve_peq) E1 += Epeq;

    //printf("\nE1:=%f\n", E1);

    /*!   Q-Chem implementation (Revised Aug/2007 KST) HF-SCRF with Multipole Expantion
     *    ( CCSD-SCRF implementation is also implemented in ccman() )
     *    Ref:- L. Onsager, J. Am. Chem. Soc. (1936), 58, 1486.
     *          H. Agren, C.M. LLanos, K.V. Mikkelsen, Chem. Phys. (1985),115, 43.
     *          K.V. Mikkelsen, et. al., J. Chem. Phys. (1988), 89, 3086.
     *
     *    // **Reaction Field Theory** //
     *
     *    E       =  E_{vac} + E_{sol}
     *    E_{sol} = -\frac{1}{2} \sum_{lm} Q_{lm} \cdot R_{lm}
     *    R_{lm}  = g \cdot Q_{lm}
     *    g       = \frac{(l+1)(\epsilon-1)}{l+(l+1)\epsilon}\frac{1}{a_0^{2l+1}}
     *    Rf      = g.R_{lm}
     *    F_mu    = F_0 +  Rf.M_{lm}
     *
     *    a_0 = radius of the spherical cavity
     *    \epsilon  = dielectric constant
     *    Q_{lm} = multipole moment
     *    l = order of the multipole moment.
     *    Rf = reaction field
     *    M_{lm} = multipole momnet integrals in pure sherical harmonics
     *
     *    at this pont pure sherical hamonics multipole moment integrals are already
     *    calculated in mkSTV.C and saved on the disk
     */

    //:~:
    if (useKirkwood){
      int i,j,k,l, lmin,lmax;
      int NMMp =  LFuncP(0,MulOrd);
      int NMMc =  LFuncC(0,MulOrd);
      double *MulMomentsP = QAllocDouble(NMMp);
      double *RFieldC     = QAllocDouble(NMMc);
      jFsol = QAllocDouble(NB2);
      VRload(jFsol,NB2,0.0);
      ESolv  = 0.0;

      // Calculates Solvent Multipole Moments
      double *jMMmat = QAllocDouble(NB2);
      FileMan_Open_Read(FILE_SOL_MULT_MATRIX);
      for(l=1;l<=MulOrd;l++){
	lmin = l*l;
	lmax = (l+1)*(l+1)-1;
	for(k=lmin;k<=lmax;k++){
	  FileMan(FM_READ,FILE_SOL_MULT_MATRIX,FM_DP,NB2,NB2*k,FM_BEG,jMMmat);
	  VMtrace(&MulMomentsP[k],jPAv,jMMmat,True);
	  MulMomentsP[k] = jMMnuc[k] - MulMomentsP[k];

	  if(rem_read(REM_SCF_UPDATE_RXN_FIELD))
	    RField[k] = g[l] * MulMomentsP[k];

	  // Calculates the solvnt energy
	  ESolv -= 0.5 * RField[k] * MulMomentsP[k];

	  // Builds solvent fock matrix .
	  VRaxpy(jFsol,RField[k],jMMmat,jFsol,NB2);
	}
      }
      FileMan_Close(FILE_SOL_MULT_MATRIX);
      if (jMMmat) QFree(jMMmat);

      // adds solvent fock matrix to one electron fock matrix
      VRadd(jHv,jHv,jFsol,NB2);

      // write one electron matrix as h = T + V + Fsol, needs in CCSD ref
      FileMan(FM_WRITE,FILE_1E_SOL_MATRIX,FM_DP,NB2,0,FM_BEG,jHv);

      // Write solvent reation field on the disk if we created it in scfman()
      // do we realy need this write on disk? check??
      if(rem_read(REM_SCF_UPDATE_RXN_FIELD))
	FileMan(FM_WRITE,FILE_SOL_RXN_FIELD,FM_DP,NMMp,0,FM_BEG,RField);

      double E_Solv = ESolv;
      std::cout << "ESolv = " << ESolv << "\n";
      FileMan(FM_WRITE,FILE_SOL_ENERGY,FM_DP,1,1,FM_BEG,&E_Solv);

      /*
      // FOR NOW WE comment this piece of code
      // whic calculates reaction fied for 1stdrv gradient
      // right now only L=1 works for 1stdrv gradient

      // for Gradient stuff;  psh --> cart
      PSH2Cartvec(RFieldC,NMMc,RField,NMMp,MulOrd,NMMp,NMMc);

      MultipoleField MField;
      for(int i=1; i<=MulOrd; i++)
	for(int j=LFuncC(0,i-1); j<LFuncC(0,i); j++)
	  MField.Add(j+1,RFieldC[j]);

      //Correct for Nucleus-Field interaction
      double* jA;
      INTEGER *iAtNo,NAtoms;
      get_carts(NULL,&jA,&iAtNo,&NAtoms);
      double ENucField = MField.NuclearInteractionEnergy(jA,iAtNo,NAtoms);
      //E1+=ENucField; // we add to total energy

      MField.WriteToDisk(FILE_MULT_FIELD2);
      */

      // This works for L=1 for now, to be fixed
      // FILE_MULT_FIELD2 will read in gradient code
      // RField in pure(sphericl)
      MultipoleField MField;
      MField.Add(2,RField[3]);
      MField.Add(3,RField[1]);
      MField.Add(4,RField[2]);
      MField.WriteToDisk(FILE_MULT_FIELD2, FILE_MULT_FIELD2_COEF);

      if (IPrint >= 2){
	cout.precision(12); // **
	for(l=0; l<=MulOrd; l++)
	  {
	    lmin = l*l;
	    lmax = (l+1)*(l+1)-1;
	    double Es = 0.0;
	    j = 0;
	    for(i=lmin; i<=lmax;i++)
	      {
		Es = -0.5 * RField[i] * MulMomentsP[i];
		printf("l,m (%d,%d)",l,j-l);
		cout <<"\n==================\n";
		cout <<"  Es(l,m), Q(lm) = "<<Es<<"  "<< MulMomentsP[i]<<endl;
		cout <<"  RF(l,m)        = "<<RField[i]<<endl<<endl;
		j++;
	      }
	  }
	SetDefaultFPFormat(cout); // **
	cout <<endl;
	//cout << "ENucField = "<<ENucField <<endl;
	MatPrint(jFsol,-1,"Solvent Fock Matrix");
      } //if (IPrint >= 2) close

      if (jFsol) QFree(jFsol);
    } // close if(useKirkwood)


    //AML,RDA
    double* jVv;
    EV = 0; // MSL 3/99 - If we don't decompose then EV is undefined
    // do it always so kinetic energy can be calculated for virial ratio.
    //    if (DecompJ) {
    jVv = OneEMtrx().getV();
    VMtrace(&EV,jPAv,jVv,True);
    //    }


    /* Fock (J and/or K) build starts here, except that on the first cycle
       we might extrapolate instead.  In that case the energy decomposition
       is meaningless until we do a proper build. */

    if (ExtrapFock && IteSCF == 1){
       BuildFock=FALSE;
#ifdef DEVELOPMENT
       printf("Extrapolated Fock matrix used in lieu of Fock build\n");
#endif
    }
    else BuildFock=TRUE;

    qtime_t Timer4Build=QTimerOn();
    double Time4Build[3];


    /* The J matrix is held in sparse form, but for now the K matrices
       are held in square form !!! */

    // Initializes IncFock and VarThresh data......

    //RST: time scf
    qtime_t rusty20;
    double rusty21[3];
    rusty20 = QTimerOn();

    SCFConv.NextCycle(IteSCF,Matrix2E,EMax,MetSCF);

    LOGICAL UseIncFock = SCFConv.UseIncFock();

    if (UseIncFock && jdPv == NULL) {
      jdPv    = QAllocDoubleWithInit(NB2car);
      jdJv    = QAllocDoubleWithInit(NB2car);
      jPvlast = QAllocDoubleWithInit(NB2car);
      jJvlast = QAllocDoubleWithInit(NB2car);
      if( (XCFunc.HasHF() || add_LRK || LRC) || (dc_dft && XCFunc.IsPureDFT() && !have_hfdens) || 
         (dscf_eda && XCFunc.IsPureDFT() && !have_hfdens))
      {
	jdPA    = QAllocDoubleWithInit(NBas6D*NBas6D*NDen);
	jdPB    = jdPA    + NBas6D*NBas6D*(NDen-1);
	jdKA    = QAllocDoubleWithInit(NBas6D*NBas6D*NDen);
	jdKB    = jdKA    + NBas6D*NBas6D*(NDen-1);
	jPAlast = QAllocDoubleWithInit(NBas6D*NBas6D*NDen);
	jPBlast = jPAlast + NBas6D*NBas6D*(NDen-1);
	jKAlast = QAllocDoubleWithInit(NBas6D*NBas6D*NDen);
	jKBlast = jKAlast + NBas6D*NBas6D*(NDen-1);
        if (XCFunc.HasHF() && LRC){
           jdKAsr = QAllocDoubleWithInit(NBas6D*NBas6D*NDen);
           jdKBsr = jdKAsr + NBas6D*NBas6D*(NDen-1);
           jKAsrLast = QAllocDoubleWithInit(NBas6D*NBas6D*NDen);
           jKBsrLast = jKAsrLast + NBas6D*NBas6D*(NDen-1);
        }
      }
    }

    LOGICAL UseIntScreen = SCFConv.UseIntScreen();
    LOGICAL Use_dP       = SCFConv.Use_dP();
    #if(JMHDEBUG)
       cout << "JMH: UseIntScreen = " << UseIntScreen << endl;
       cout << "JMH: Use_dP = " << Use_dP << endl;
    #endif
    double  VThresh = SCFConv.VThresh();

    /* J, K, and H parts of Fock build */
    // Begin building Fock matrix
    if (BuildFock && rem_read(REM_ROKS)==0){
       if (DoJ && ((!dc_dft && !dscf_eda) || (dc_dft && have_hfdens) || (dscf_eda && have_hfdens)))
       {

         //TRA - Incremental Fock J only....real work starts here......

         // Calculate an incremental Fock matrix from the dP
         if(Use_dP) {

           #ifdef DEVELOPMENT
             printf("Using dP: J\n");
           #endif
           VRsub(jdPv,jPAv,jPvlast,NB2car);

	       // Calculate Coulomb Matrix (jJv) with incfock = true
           MakeJ(jdJv,jdPv,1,IPrint-2,NDeriv,VThresh,UseIntScreen,Use_dP,IteSCF!=1);
           VRadd(jJv,jJvlast,jdJv ,NB2car);
         }
         else {

           #ifdef DEVELOPMENT
             if(UseIntScreen) printf("Using Integral Screening\n");
           #endif
	       // BJA_J: Calculating Coulomb Matrix (jJv) without incfock = false
               // Calculate jJfrg12v and set jJv = jJfrg12v - jJv
               if(rem_read(REM_EMBED_INTERNAL)){
                 MakeJ(jJv,jPAfrg12v,1,IPrint-2,NDeriv,VThresh,UseIntScreen,Use_dP,IteSCF!=1);

                 double * jSv = QAllocDoubleWithInit(NB2);
                 double elecs = 0.0;
                 double elecsv = 0.0;
                 ScaV2M(jS,jSv,True,False);
                 VMtrace(&elecsv,jPAfrg12v,jSv,True); // Only want coulomb contrib. from frg 1
                 matTrace2(elecs, jS, jPAfrg12, NBasis, NBasis);
#ifdef DEVELOPMENT
                 if (IPrint >= 1) {
                    cout << "NAlpha = " << NAlpha << endl;
                    cout << "elecs = " << elecs << endl;
                    cout << "elecsv = " << elecsv << endl;
                 }
#endif
               } else {
                 MakeJ(jJv,jPAv,1,IPrint-2,NDeriv,VThresh,UseIntScreen,Use_dP,IteSCF!=1);
	           }

         }

         // Save Last P and J for IncFock........

         if(UseIncFock) {
           VRcopy(jPvlast,jPAv,NB2car);
           VRcopy(jJvlast,jJv ,NB2car);
         }
       }
       else if (XCFunc.HasHF() || add_LRK || LRC ||
               (!(XCFunc.HasHF() && add_LRK && LRC) && dc_dft && !have_hfdens) ||
               (!(XCFunc.HasHF() && add_LRK && LRC) && dscf_eda && !have_hfdens))
       {

         jKA = QAllocDouble2(NBas6D*NBas6D*NDen,shared);
         jKB = jKA + NBas6D*NBas6D*(NDen-1);
         VRload(jKA,NBas6D*NBas6D*NDen,0.0);
         if (XCFunc.HasHF() && LRC){
            // long-range K (jKA) and short-range K (jKAsr) stored separately
	    if(jKAsr==NULL) // EJS Memleak fix
	    {
               jKAsr = QAllocDouble2(NBas6D*NBas6D*NDen,shared);
	    }
            jKBsr = jKAsr + NBas6D*NBas6D*(NDen-1);
         }


         //TRA - Incremental Fock J & K ....real work starts here......

         if(Use_dP && ((!dc_dft && !dscf_eda) || (dc_dft && have_hfdens) || (dscf_eda && have_hfdens))) 
         {
           #ifdef DEVELOPMENT
	      printf("Using dP: JK\n");
           #endif
	   VRsub(jdPv,jPAv,jPvlast,NB2car);
	   VRsub(jdPA,jPA,jPAlast,NBas6D*NBas6D);
           if (NDen == 2) VRsub(jdPB,jPB,jPBlast,NBas6D*NBas6D);

           if ((add_LRK || LRC) && ((!dc_dft && !dscf_eda) || (dc_dft && have_hfdens) || (dscf_eda && have_hfdens))) 
           {
              // Separate J & K builds for long-range-corrected DFT
             #ifdef DEVELOPMENT
	        cout << " Building regular ol' J (Use_dP version)\n";
             #endif
             MakeJ(jdJv,jdPv,1,IPrint-2,NDeriv,VThresh,UseIntScreen,
                   Use_dP,IteSCF!=1);

             // long-range K
             if (add_LRK)
                rem_write(OP_XTERFG,REM_INTEGRAL_2E_OPR);
             else{
                rem_write(OP_ERF,REM_INTEGRAL_2E_OPR);
                #ifdef DEVELOPMENT
                   printf(" Building long-range K (w = %.3e)\n",omega);
                #endif
             }
             MakeK(jdKA,jdKB,jdPA,jdPB,IPrint-2,NDeriv,VThresh,UseIntScreen,Use_dP);
            if (!(rem_read(REM_COMBINE_K)==1 || ri_comb_k)){
                VRscale(jdKA,N2,hfx_lr_coef);
                if (NDen == 2) VRscale(jdKB,N2,hfx_lr_coef);
             }

             // short-range K, if the base functional is a hybrid
             if (LRC && XCFunc.HasHF() && rem_read(REM_COMBINE_K) != 1){
                #ifdef DEVELOPMENT
                   cout << " Building short-range K (Use_dP version)\n";
                #endif
                rem_write(OP_ERFC,REM_INTEGRAL_2E_OPR);
                MakeK(jdKAsr,jdKBsr,jdPA,jdPB,IPrint-2,NDeriv,VThresh,
                      UseIntScreen,Use_dP);
                VRscale(jdKAsr,N2,XCFunc.KCof());
                if (NDen == 2) VRscale(jdKBsr,N2,XCFunc.KCof());
             }

             rem_write(OP_R12,REM_INTEGRAL_2E_OPR);
           }
           else {
             // no LRC -- standard code for hybrids
             MakeJK(jdJv,jdKA,jdKB,jdPv,jdPA,jdPB,IPrint-2,NDeriv,VThresh,UseIntScreen,Use_dP,IteSCF!=1);
             VRscale(jdKA,N2,XCFunc.KCof());
             if (NDen == 2) VRscale(jdKB,N2,XCFunc.KCof());
           }
	   VRadd(jJv,jJvlast,jdJv ,NB2car);
           // Bhaskar Rana: fix DC-DFT for hybrids
           if(dc_dft && have_hfdens) 
           {
              VRscale(jKAlast,N2,XCFunc.KCof());
              if (NDen == 2) VRscale(jKBlast,N2,XCFunc.KCof());
           }
           // end Bhaskar 
	   VRadd(jKA,jKAlast,jdKA ,NBas6D*NBas6D);
	   if (NDen == 2) VRadd(jKB,jKBlast,jdKB ,NBas6D*NBas6D);
           if (XCFunc.HasHF() && LRC){
              VRadd(jKAsr,jKAsrLast,jdKAsr,NBas6D*NBas6D);
              if (NDen == 2) VRadd(jKBsr,jKBsrLast,jdKBsr,NBas6D*NBas6D);
           }
         }
         else {
#ifdef DEVELOPMENT
	   if(UseIntScreen) printf("Using Integral Screening\n");
#endif
           if ((add_LRK || LRC) && ((!dc_dft && !dscf_eda) || (dc_dft && have_hfdens) || (dscf_eda && have_hfdens))) 
           {
             // Separate J & K builds for long-range-corrected DFT
             #ifdef DEVELOPMENT
                cout << " Building regular ol' J (integral screening version)\n";
             #endif
             MakeJ(jJv,jPAv,1,IPrint-2,NDeriv,VThresh,UseIntScreen,Use_dP,IteSCF!=1);

             // long-range K
             if (add_LRK)
                rem_write(OP_XTERFG,REM_INTEGRAL_2E_OPR);
             else if(!ri_comb_k)
                rem_write(OP_ERF,REM_INTEGRAL_2E_OPR);

	     //The isotropic scaling of the LR
             //INTEGER Isepsilon_r = rem_read(REM_ANISO_SRSH) == -101;
             INTEGER Isepsilon_r = rem_read(REM_ANISO_SRSH) == 1;
	     if (!Isepsilon_r)     (Isepsilon_r = rem_read(REM_ANISO_SRSH) == -102);
	     if (!Isepsilon_r)     (Isepsilon_r = rem_read(REM_ANISO_SRSH) == -103);

	     if (Isepsilon_r) {
		INTEGER NAtoms = rem_read(REM_NATOMS);
	        INTEGER *IBasOffAtom = QAllocINTEGER(2*NAtoms);
		BasisSet S1(rem_read(REM_IBASIS));
	        INTEGER NShl = S1.NShell();
                INTEGER iBas = 0;
		for(INTEGER iShl = 0; iShl<NShl; iShl++) {
	           INTEGER iBasOff = S1.ShellStart(iShl);
		   INTEGER iShlCen = S1.pShellCen()[iShl];
	           if (iShl > 0) {
                    if (iShlCen > S1.pShellCen()[iShl-1]){
                         IBasOffAtom[iShlCen-1]=iBasOff;
		            }
		         }
		         else {
			  IBasOffAtom[0]=0;
			  IDC1 = rem_read(REM_ANISO_SRSH_EPS1);
			  IDC2 = rem_read(REM_ANISO_SRSH_EPS2);
	                  InterM = rem_read(REM_ANISO_SRSH_INTERFACE_ATOM);
			     }  //else
			  }     //for
		          inter_basis = IBasOffAtom[InterM-1];
			  rem_write(REM_ANISO_SRSH_INTATOM,inter_basis);
	                  QFree(IBasOffAtom);
	     }


             if(!SRC) 
             {
               #ifdef DEVELOPMENT
	          printf(" Building long-range K (w = %.3e)\n",omega);
               #endif
               MakeK(jKA,jKB,jPA,jPB,IPrint-2,NDeriv,VThresh,UseIntScreen,Use_dP,XCFunc.KCof(),hfx_lr_coef);
               if (!(rem_read(REM_COMBINE_K)==1 || ri_comb_k))
               {
                  VRscale(jKA,N2,hfx_lr_coef);
                  if (NDen == 2) VRscale(jKB,N2,hfx_lr_coef);
               }

               // short-range K, if the base functional is a hybrid
               if (LRC && XCFunc.HasHF() && rem_read(REM_COMBINE_K) != 1 && !ri_comb_k){
                  #ifdef DEVELOPMENT
                     cout << " Building short-range K\n";
                  #endif
                  rem_write(OP_ERFC,REM_INTEGRAL_2E_OPR);
                  MakeK(jKAsr,jKBsr,jPA,jPB,IPrint-2,NDeriv,VThresh,UseIntScreen,Use_dP);
                  VRscale(jKAsr,N2,XCFunc.KCof());
                  if (NDen == 2) VRscale(jKBsr,N2,XCFunc.KCof());
               }
             }else{ // SRC
               // LONG RANGE PART: ERF, OMEGA2, LR_HF
               int Om1=rem_read(REM_OMEGA);
               int Om2=rem_read(REM_OMEGA2);
               rem_write(Om2,REM_OMEGA);
               #ifdef DEVELOPMENT
                  printf("Building long-range K (w = %.3e)\n",omega2);
               #endif
               if (Isepsilon_r) 
               {
                  double *jPAin, *jPBin;
                  jPAin = QAllocDouble(N2*NDen);
		  jPBin = jPAin + N2*(NDen-1);
		  VRcopy(jPAin, jPA, N2*NDen);
                  if (NDen == 2) VRcopy(jPBin, jPB, N2*NDen);
		  if (inter_basis<0) QCrash("Error in anisotropic interface");
                  Scale_by_dielectric(jPAin,jPBin,NBasis,inter_basis,IDC1,IDC2,NDen);
		  rem_write(OP_ERF,REM_INTEGRAL_2E_OPR);
		  MakeK(jKA,jKB,jPAin,jPBin,IPrint-2,NDeriv,VThresh,UseIntScreen,Use_dP);
		  QFree(jPAin);
		  Scale_by_dielectric(jKA,jKB,NBasis,inter_basis,IDC1,IDC2,NDen);
               }else{
                  MakeK(jKA,jKB,jPA,jPB,IPrint-2,NDeriv,VThresh,UseIntScreen,Use_dP);
                  VRscale(jKA,N2,ScaleLR);
                  if (NDen == 2) VRscale(jKB,N2,ScaleLR);
               }

               //SHORT RANGE PART: ERFC, OMEGA1, SR_HF
               rem_write(Om1,REM_OMEGA);
               rem_write(OP_ERFC,REM_INTEGRAL_2E_OPR);
               #ifdef DEVELOPMENT
                  printf("Building short-range K (w = %.3e)\n",omega);
               #endif
               MakeK(jKAsr,jKBsr,jPA,jPB,IPrint-2,NDeriv,VThresh,UseIntScreen,Use_dP);
               VRscale(jKAsr,N2,ScaleSR);
               if (NDen == 2) VRscale(jKBsr,N2,ScaleSR);
             }

             rem_write(OP_R12,REM_INTEGRAL_2E_OPR);
           }
           else {
             // no LRC -- standard code for hybrids
             if (do_makeJ && IteSCF == 1){
                MakeJ(jJv,jPAv,1,IPrint-2,NDeriv,VThresh,UseIntScreen,Use_dP,IteSCF!=1);
                do_makeJ = 0;
             }
             MakeJK(jJv,jKA,jKB,jPAv,jPA,jPB,IPrint-2,NDeriv,VThresh,UseIntScreen,Use_dP,IteSCF!=1);
             if ((!dc_dft && !dscf_eda) || (dc_dft && have_hfdens) || (dscf_eda && have_hfdens))
             {
                VRscale(jKA,N2,XCFunc.KCof());
                if (NDen == 2) VRscale(jKB,N2,XCFunc.KCof());
             }
           }
         }

         // Save Last P, J, and K for IncFock........

         if(UseIncFock) {
	   VRcopy(jPvlast,jPAv,NB2car);
	   VRcopy(jJvlast,jJv ,NB2car);
	   VRcopy(jPAlast,jPA ,NBas6D*NBas6D);
	   if (NDen == 2) VRcopy(jPBlast,jPB ,NBas6D*NBas6D);
	   VRcopy(jKAlast,jKA ,NBas6D*NBas6D);
	   if (NDen == 2) VRcopy(jKBlast,jKB ,NBas6D*NBas6D);
           if (XCFunc.HasHF() && LRC){
              VRcopy(jKAsrLast,jKAsr,NBas6D*NBas6D);
              if (NDen == 2) VRcopy(jKBsrLast,jKBsr,NBas6D*NBas6D);
           }
         }

       }

	   // Coulomb (J) energy calculated from jPAv matrix
         if ((dc_dft && have_hfdens) || (dscf_eda && have_hfdens)) VRcopy(jJv,jJv_temp,NB2car*NDen);
         VMtrace(&EJ,jPAv,jJv,True);
         EJ *= 0.5;
         if (DecompJ)printf("Total value           of EJ %22.13f\n", EJ);



      if ( (XCFunc.HasHF() || add_LRK || LRC) || (dc_dft && XCFunc.IsPureDFT() && !have_hfdens) || 
           (dscf_eda && XCFunc.IsPureDFT() && !have_hfdens)) 
      {
         FileMan(FM_WRITE,FILE_EXCHANGE_MATRIX,FM_DP,NDen*NBas6D*NBas6D,0,FM_BEG,jKA);
         VRdot(&EKA,jPA,jKA,N2);
         if (NDen == 2)
           VRdot(&EKB,jPB,jKB,N2);
         else
           EKB = EKA;
         EKA *= 0.5;
         EKB *= 0.5;
         if (XCFunc.HasHF() && LRC && rem_read(REM_COMBINE_K) != 1 && !ri_comb_k){
            VRdot(&EKAsr,jPA,jKAsr,N2);
            if (NDen == 2)
               VRdot(&EKBsr,jPB,jKBsr,N2);
            else
               EKBsr = EKAsr;
            EKAsr *= 0.5;
            EKBsr *= 0.5;
            EKA += EKAsr;
            EKB += EKBsr;
         }
       }
       else{
         EKA = EKB = 0.0;
         EKAsr = EKBsr = 0.0;
       }

		 // if we have exchange energy density in functional part, we
		 // need to store the exchange energy so that to make comparision
		 if (XCFunc.HasExchVar()) {
			 FileMan(FM_WRITE,FILE_EXCHANGE_ENERGY,FM_DP,1,0,FM_BEG,&EKA);
			 FileMan(FM_WRITE,FILE_EXCHANGE_ENERGY,FM_DP,1,0,FM_CUR,&EKB);
		 }


       if (IPrint >= 3) {
         MatPrint(jJv,-1,"Coulomb Matrix");
         if ( (XCFunc.HasHF() || add_LRK || LRC) || (dc_dft && XCFunc.IsPureDFT() && !have_hfdens) || 
              (dscf_eda && XCFunc.IsPureDFT() && !have_hfdens)) 
         {
           if ( !(LRC && XCFunc.HasHF()) ){
              MatPrint(jKA,N,N,"Alpha Exchange Matrix");
              if (NDen == 2) MatPrint(jKB,N,N,"Beta Exchange Matrix");
           }
           else{
              MatPrint(jKA,N,N,"Long-Range Alpha Exchange Matrix");
              MatPrint(jKAsr,N,N,"Short-Range Alpha Exchange Matrix");
              if (NDen == 2){
                 MatPrint(jKB,N,N,"Long-Range Beta Exchange Matrix");
                 MatPrint(jKBsr,N,N,"Short-Range Beta Exchange Matrix");
              }
           }
         }
       }

       /* Form the contribution from H and J to the Fock matrix. */

       // BJA_FOCK!: Adding in Jfrg12 to square fock matrix
         VRadd(jFAv, jHv, jJv, NB2);

       if (NDen == 2) VRcopy(jFBv,jFAv,NB2);

       if (usingNEGF) { //save necessary data into files
	 double* tempJ;
	 tempJ = QAllocDouble(N2);
	 ScaV2M(tempJ,jJv,True,True);
	 rw_disc_trans_1D_double(&tempJ[0],N2,"NEGF_Jmat.tmp","save");
	 QFree(tempJ);
	 if(IteSCF==1){
	   double* tempH;
	   tempH = QAllocDouble(N2);
	   ScaV2M(tempH,jHv,True,True);
	   rw_disc_trans_1D_double(&tempH[0],N2,"NEGF_hmat.tmp","save");
	   QFree(tempH);
	 }
       }

    }  /* Finished J, K, and H parts of Fock build */

    else if ((XCFunc.HasHF() || add_LRK || LRC) || (dc_dft && XCFunc.IsPureDFT() && !have_hfdens) || 
             (dscf_eda && XCFunc.IsPureDFT() && !have_hfdens))
    {
       // If we skipped the Fock build then these need to be allocated
       jKA = QAllocDouble2(NBas6D*NBas6D*NDen,shared);
       jKB = jKA + NBas6D*NBas6D*(NDen-1);
       if (XCFunc.HasHF() && LRC){
	 if(jKAsr == NULL) // AJWT && EJS added to fix mem leak
         {
	    jKAsr = QAllocDouble2(NBas6D*NBas6D*NDen,shared);
	 }
         jKBsr = jKAsr + NBas6D*NBas6D*(NDen-1);
       }
    }

#ifdef RUSTY
    //RST: time scf
    QTimerOff(rusty21,rusty20);
    printf("TIMEINFO->: J/JK contribution %.2f sec.\n",rusty21[0]);
#endif

    /* Call ChemSol self-consistently */
    INTEGER CSStart = 6, CSPeriod = 3;

    if (rem_read(REM_CHEMSOL) == 1 && IteSCF >= CSStart
        && (IteSCF-CSStart)%CSPeriod==0 ) {
      // Calculate Mulliken charges for ChemSol's use
      INTEGER NAtoms = rem_read(REM_NATOMS);
      double* AtomicCharges = qalloc_double(NAtoms);
      MullCharge(AtomicCharges,jPAv);
      qfree(AtomicCharges);
      LOGICAL Final = FALSE;
      ChemSol(jPAv,eNucSolvnt,eSolvnt,Final);
    }
    if (rem_read(REM_CHEMSOL) == 1 && IteSCF >= CSStart
        && (IteSCF-CSStart)%CSPeriod==1 ) {
      diisControl.Reset(0);
      eNucSolvnt_old = eNucSolvnt;
      eSolvnt_old = eSolvnt;
      }

    if (IteSCF == 1 && rem_read(REM_CDFTCI)) diisControl.Reset(0);

    /* The part of the calculation requiring the total density matrix
       is over:  now we need the individual density matrices.  Split
       them apart again. */

    if (NDen == 1) {
      VRscale(jPAv,NB2,0.5);
      // Since we are doing jPAfrg12v - jPAv, we want both to be scaled equivalently
      // BJA_P!
      if(rem_read(REM_EMBED_INTERNAL)){
        VRscale(jPAfrg2v, NB2, 0.5);
        VRadd(jPAfrg12v,jPAv,jPAfrg2v,NB2);
      }
    }
    else {
      VRsub(jPAv,jPAv,jPBv,NB2);
      if(rem_read(REM_EMBED_INTERNAL)){
        //VRadd(jPAfrg2v, jPAfrg2v, jPAfrg2v+NB2 ,NB2);
        //VRadd(jPAfrg12v, jPAv,jPAfrg2v ,NB2);
        //ScaV2M(jPAfrg12,jPAfrg12v,True,True);
        VRsub(jPAfrg2v, jPAfrg2v, jPBfrg2v, NB2);
        VRadd(jPAfrg12v, jPAv,jPAfrg2v ,NB2);
        VRadd(jPBfrg12v, jPBv,jPBfrg2v ,NB2);
        ScaV2M(jPAfrg12,jPAfrg12v,True,True);
        ScaV2M(jPBfrg12,jPBfrg12v,True,True);
      }
    }

    //RST: time scf
    qtime_t rusty30;
    double rusty31[3];
    rusty30 = QTimerOn();

    /* Form the XC contributions */

    if ((BuildFock && !rem_read(REM_ROKS)) && ((!dc_dft && !dscf_eda) || (dc_dft && have_hfdens) || 
        (dscf_eda && have_hfdens))) 
    {
      double Esm=0.0;
      if(do_mrXC || do_FTC) {
	if(do_mrXC) {
	  mrxc_ini(); // mrXC_exit part of grid_exit
	  if (interp_grid == 0) {
	    IGrdDF = rem_read(REM_IGRDTY);
	    interp_grid = new local_interp(XCFunc,IGrdDF,NDen,0);
	  } // interp_grid
	} // do_mrXC

	// BJA_XC: calculate Exchange-Correlation Matrix with mrXC = true and FTC = true
    // Plan to calc. with jPAfrg12v
	fftJnXC(Esm, jJv, jPAv, ShlPrs(DEF_ID), NDen, do_mrXC);  //No incremental!
	if(do_FTC) {
	  VRadd2(jFAv,jJv,NB2);
	  if (NDen == 2) VRadd2(jFBv,jJv,NB2);
	  EJ += Esm;
	} // do_FTC
      } // do_mrXC or do_FTC
    if (XCFunc.HasDFT()) 
    {
      INTEGER iNLC = rem_read(REM_NL_CORRELATION);
      if(do_mrXC) 
      {
        if (iNLC > 0) QCrash("Nonlocal correlation does not work with mrXC");

	// BJA_XC: calculate Exchange-Corelation Matrix with DFT && mrXC = true
        // Plan to calc. with jJfrg12v
        DFTman_mrxc(&EX,&EC,jXCAv,jXCBv,jPAv,jCAXC,NULL,NULL,2,XCFunc,interp_grid,IGrdDF,IPrint-2,IteSCF, EMax);
      } 
      else {
        // lambda-dependent functional, we store the exchange Fock matrix first
        if (XCFunc.hasLambdaFunc()) 
        {
          // however, here we note that we need transform it into vector form
          double * jKAv = QAllocDouble(NB2car*NDen);
          ScaV2M(jKA,jKAv,True,False);
          if (NDen == 2) {
             double * jKBv = jKAv + NB2car;
             ScaV2M(jKB,jKBv,True,False);
          }
          FileMan(FM_WRITE,FILE_EXCH_LAMBDA_FUNC,FM_DP,NB2car*NDen,0,FM_BEG,jKAv);
          //MatPrint(jKAv, 1, NB2car, "final exchange matrix in vector");
          QFree(jKAv);

          // store the EKA and EKB
          FileMan(FM_WRITE,FILE_EXCH_LAMBDA_FUNC,FM_DP,1,NB2car*NDen,FM_BEG,&EKA);
          if (NDen == 2) {
             FileMan(FM_WRITE,FILE_EXCH_LAMBDA_FUNC,FM_DP,1,NB2car*NDen+1,FM_BEG,&EKB);
          }
          //printf ("in scfman, EKA is %f, EKB is %f\n", EKA, EKB);

        }
        //INTEGER IGrdDF_2;

	// standard DFT (FTC is often turned on, turn off with FTC = false)
        if (XCFunc.NumExch()>0 || XCFunc.NumCorr()>0) { // if there is only NLC then NExch=NCorr=0, but HasDFT()=TRUE
          IGrdDF_2 = pick_grid(rem_read(REM_IGRDTY),EMax,IteSCF,NBasis);
          rem_write(pick_XC_thresh(IGrdDF_2!=rem_read(REM_IGRDTY),EMax,Cnverg),REM_DFT_THRESH);

	      // BJA_XC!: calculate Exchange-Correlation Matrix with DFT && mrXC = false // Calculating jXCAv and jXCfrg12v and setting jXCAV = jXCfrg12v - jXCAv
          // DFTman called for FTC off and mrXC off, with pure DFT

          if(rem_read(REM_EMBED_INTERNAL)) {
              DFTman(&EX,&EC,jXCAv,jXCBv,jPAfrg12v,jCAXC,NULL,NULL,2,
                XCFunc,IGrdDF_2,IPrint-2,IteSCF, EMax);
          } else {
              DFTman(&EX,&EC,jXCAv,jXCBv,jPAv,jCAXC,NULL,NULL,2,
                XCFunc,IGrdDF_2,IPrint-2,IteSCF, EMax);
          }
        }
        if (iNLC > 0) {
          // nonlocal correlation may use a different grid and therefore has to be computed separately
          if (!ClosedShell() && (iNLC == NLCFUNC_vdWdf04 || iNLC == NLCFUNC_vdWdf10))
            QCrash("vdW-DF is not defined for open shells");
          double *jNLAv, *jNLBv;
          if (XCFunc.NumExch()>0 || XCFunc.NumCorr()>0)
            jNLAv = QAllocDouble2(NB2car*NDen,shared);
          else jNLAv = jXCAv;
          jNLBv = jNLAv + NB2car*(NDen-1);
//          printf(" Precomputing and saving data for nonlocal correlation\n");

          IGrdDF_2 = pick_grid(rem_read(REM_NL_GRID),EMax,IteSCF,NBasis);
          rem_write(pick_XC_thresh(IGrdDF_2!=rem_read(REM_NL_GRID),EMax,Cnverg),
              REM_DFT_THRESH);
          double Junk, ENLC;

	      // BJA_XC: calculate Exchange-Correlation Matrix for nonlocal correlation
          // Plan to calc. with jJfrg12v
          DFTman(&Junk,&ENLC,jNLAv,jNLBv,jPAv,jCAXC,NULL,NULL,1,
              XCFunctional(0,CFUNC_NL_Init),IGrdDF_2,IPrint-2,IteSCF,EMax);

	      // BJA_XC: calculate Exchange-Correlation Matrix for nonlocal correlation
          // Plan to calc. with jJfrg12v
          DFTman(&Junk,&ENLC,jNLAv,jNLBv,jPAv,jCAXC,NULL,NULL,2,
              XCFunctional(0,CFUNC_NL_Eval),IGrdDF_2,IPrint-2,IteSCF, EMax);
#ifdef DEVELOPMENT
          printf(" Nonlocal correlation = %16.10f\n", ENLC);
#endif
          if (XCFunc.NumExch()>0 || XCFunc.NumCorr()>0) {
            VRadd(jXCAv,jXCAv,jNLAv,NB2);
            if (NDen == 2) VRadd(jXCBv,jXCBv,jNLBv,NB2);
            QFree(jNLAv);
            EC += ENLC;
           }
          else EC = ENLC;
         }

      } // do_mrXC false

//double EEE[1];
//VMtrace(EEE,jPAv,jXCAv,True);
//printf("Tr Ra.XCa = %.10f\n",EEE[0]);
//VMtrace(EEE,jPBv,jXCBv,True);
//printf("Tr Rb.XCb = %.10f\n",EEE[0]);


       if (IPrint >= 3) {
	     MatPrint(jXCAv,-1,"Alpha XC Matrix");
   	   if (NDen == 2) MatPrint(jXCBv,-1,"Beta XC Matrix");
         }
       } // XCFunc.HasDFT
       else
         EX = EC = 0.0;

       if(do_mrXC) {
	  // BJA_XC: jPAv -> jPAplusBv
      /* Calculating Coulomb and exchange matrix using multiresolution method
      *  Turn of mrXC in the beginning
      *  Obtains density matrix from global variable
      */
	     fftJnXCMtrx(Esm, jXCAv, ShlPrs(DEF_ID), NDen, do_mrXC);
	 EX += Esm;
       }
       if ((dc_dft && have_hfdens) || (dscf_eda && have_hfdens)) have_dftE = TRUE;
    } /* Finished XC build */

#ifdef RUSTY
    //RST: time scf
    QTimerOff(rusty31,rusty30);
    printf("TIMEINFO->: XC contribution %.2f sec.\n",rusty31[0]);
#endif


    if (rem_read(REM_CHEMSOL) == 1 && IPrint >= 1) {
      printf("*** Nuclear-solvent energy = %f ***\n",eNucSolvnt_old);
      printf("*** Solvent-solvent energy = %f ***\n",eSolvnt_old);
    }

    EOld=ETot;

    /* Compute the total energy */
    if (rem_read(REM_EMBED_INTERNAL)) {
        EX *= 0.5;
        EC *= 0.5;
        // Read in ENuc from Supermolecular calc?
    }

    // Begin code to call MBD for Self Consistent Correction
    // Added by Thomas Markovich 02/2016
                // MBD = 1 means energy Only
                // MBD = 2 means energy + forces but no SC
                // MBD = 3 means energy + sc but no forces
                // MBD = 4 means energy + sc + forces
    // Modified by Szabolcs Goger 9/2022 when adding LibMBD support
        // For now, MBD = 102 is just the same as MBD = 4 (to be changed)
    INTEGER MBD = rem_read(REM_MBDVDW);
    if(((MBD==3) || (MBD==4) || (MBD==102))){
        bool do_sc = ((MBD==3) || (MBD==4) || (MBD==102));
        //bool do_force = false;
        bool do_force = ((MBD==4) || (MBD==102));
        bool do_library = false;
        compute_mbd(do_sc, do_force, do_library);
        ftn_mbdvdw_get_energy(&Edisp);
        if(do_sc){
          int nBas6D = bSetMgr.crntShlsStats(STAT_NBAS6D);
          int nBasis = bSetMgr.crntShlsStats(STAT_NBASIS);
          int nB2    = rem_read(REM_NB2);

          double* dEdP = QAllocDouble(nBas6D*nBas6D);
          VRload(dEdP, nBas6D*nBas6D, 0.0);
          compute_potential(dEdP);
          double* dEdPv = QAllocDouble(NB2car);
                                        ScaV2M(dEdP, dEdPv, True, False);
          VRadd(jFAv, jFAv, dEdPv, nB2);
          if(NDen==2) VRadd(jFBv, jFBv, dEdPv, nB2);
          QFree(dEdP);
          QFree(dEdPv);
        }
    }
    // End code to call MBD for self consistent corrections

    // Start -- ZCH
    // Insert QM/MM corrections
    if(rem_read(REM_EWALD_ON) == 1 && (rem_read(REM_QM_MM_INTERFACE)== JANUS || rem_read(REM_QM_MM_INTERFACE)==ONIOM)){
       ForceMan_Class FMan;
          static bool SCFewald = false;
          static bool FileWritten = false;
          if(IteSCF == 1 && SCFewald != false){
             SCFewald = false;
             FileWritten = false;
          }
          if(SCFewald) FileWritten = true;
          if(!FileWritten){
             VRload(jQj,NBasis*NBasis*rem_read(REM_NATOMS),0.0);
          }
          if(EMax<FMan.ewaldSCFon && rem_read(REM_IBASIS) != rem_read(REM_BASIS2)){
             if(SCFewald == false) diisControl.Reset(0);
             SCFewald=true;
          }
          if(SCFewald) EewQMMM=QMMMFock(jS,jFAv,jFBv,jPAv,jPBv,NBasis,NDen,FileWritten,jQj);
    }
    //End -- ZCH



    //ETot = ENuclear+eNucSolvnt_old+eSolvnt_old+E1+EJ+EKA+EKB+EX+EC+E_EFP+ESolv+E_born+Edisp;
    // for the lambda-dependent functional, the exchange energy is mixed into the XC part
	 // so that we do not count in directly
	 if (XCFunc.hasLambdaFunc()) {
		 ETot = ENuclear + eNucSolvnt_old + eSolvnt_old
                       + E1 + EJ + EX + EC + E_EFP + ESolv + E_born
                       + Edisp + Eairbed + xpNucMull + EewQMMM + EtsA + EtsB;
	 } else {
		 ETot = ENuclear + eNucSolvnt_old + eSolvnt_old
                       + E1 + EJ + EKA + EKB + EX + EC + E_EFP + ESolv + E_born
                       + Edisp + Eairbed + xpNucMull + EewQMMM + EtsA + EtsB;

        //BJA_JKN
#ifdef DEVELOPMENT
         if (IPrint >= 1) {
             // In the future -> more general, if Ecomponent > 0, print it
             // Possibly add rem var for iteration-wise Energy components
             printf("\n*** ********************* ***\n");
             printf("***   Energy Components   ***\n");
             printf("*** ********************* ***\n");
             printf("*** ENuc = %14.10f ***\n",ENuclear);
             //printf("*** eNucSolvnt_old = %f ***\n",eNucSolvnt_old);
             //printf("*** eSolvnt_old = %f ***\n",eSolvnt_old);
             printf("*** E1 = %16.10f ***\n",E1);
             printf("*** EJ = %16.10f ***\n",EJ);
             //printf("*** EKA = %f ***\n",EKA);
             //printf("*** EKB = %f ***\n",EKB);
             printf("*** EX = %16.10f ***\n",EX);
             printf("*** EC = %16.10f ***\n",EC);
             //printf("*** E_EFP = %f ***\n",E_EFP);
             //printf("*** ESolv = %f ***\n",ESolv);
             //printf("*** E_born = %f ***\n",E_born);
             //printf("*** Edisp = %f ***\n",Edisp);
             //printf("*** xpNucMull = %f ***\n",xpNucMull);
             printf("*** ********************* ***\n");
             printf("    ETot = %14.10f    \n",ETot);
             printf("*** IteSCF = %12d ***\n",IteSCF);
             printf("*** ********************* ***\n\n");
         }
#endif
	 }


    double E_scf=ETot;
    FileMan_Open_Write(FILE_SOL_ENERGY);
    FileMan(FM_WRITE,FILE_SOL_ENERGY,FM_DP,1,0,FM_BEG,&E_scf);
    if (do_efp) FileMan(FM_WRITE,FILE_SOL_ENERGY,FM_DP,1,1,FM_BEG,&E_EFP);
    FileMan_Close(FILE_SOL_ENERGY);
    // this is not clean enough, but it is dangerous to use the second position
    //     which can be either E_EFP or ESolv
    double Esol[6] = {eNucSolvnt_old, eSolvnt_old, E_EFP, ESolv, E_born, Edisp};
    FileMan(FM_WRITE,FILE_SOL_ENERGY,FM_DP,6,2,FM_BEG,Esol);
    FileMan_Close(FILE_SOL_ENERGY);

    // Kirkwood-Onsager SCF-SCRF code :~:
    if (useKirkwood)
      {

        if (IPrint >= 1) {
          if(rem_read(REM_TAO_DFT)>0){
            printf(" Minus  Theta * Entropy = %16.12f\n",EtsA + EtsB);}
            printf(" One-Electron    Energy = %16.12f\n",E1);
            printf(" Total E_JK      Energy = %16.12f\n",EJ+EKA+EKB);
            printf(" ELECTRONIC      Energy = %16.12f\n",E1+EJ+EKA+EKB);
            printf(" Nuclear Repu.   Energy = %16.12f\n",ENuclear);
            printf(" Solvation       Energy = %16.12f\n",ESolv);
            printf(" Born            Energy = %16.12f\n",E_born);
            printf(" total no solv.  Energy = %16.12f\n",ETot-ESolv-E_born);
            printf(" TOTAL           Energy = %16.12f\n",ETot);
        }

        // we write on this b/c ccman needs E_refsolv
        // need to change
        double E_tot = ETot;
        FileMan_Open_Write(FILE_SOL_ENERGY);
        FileMan(FM_WRITE,FILE_SOL_ENERGY,FM_DP,1,0,FM_BEG,&E_tot);
        FileMan_Close(FILE_SOL_ENERGY);
      }

//printf("*** Solvent = %.10f\n",eNucSolvnt_old+eSolvnt_old);
//printf("*** Nuclear = %.10f\n",ENuclear);
//printf("*** One-ele = %.10f\n",E1);
//printf("*** Coulomb = %.10f\n",EJ);
//printf("*** HFExcha = %.10f\n",EKA+EKB);
//printf("*** DFTExch = %.10f\n",EX);
//printf("*** DFTCorr = %.10f\n",EC);
//printf("*** ENtotal = %.10f\n",ETot);

    DEMax = fabs(ETot-EOld);


    if(usingNEGF){
      EMax = DEMax;
      rw_disc_trans_1D_double(&EMax,1,"NEGF_EMax.tmp","save");

      if( IteSCF == 1) {
	if(iVbias==0) {
	  //Cnverg  = TenMin(KonSCF);
	  Cnverg_NEGF = Cnverg;
	  Cnverg = -1.0;   // In NEGF, energy error is not measure of SCF convergence
	  printf("In NEGF, SCF converges DIIS maximum error for density matrix element is below %1.2e\n",Cnverg_NEGF);
	  printf("         (not error of energy) \n");
	}
	// set(update) bias voltage
	if(tran_opt==4) trans_get_Vbias(&Vbias, &iVbias,"update");
    }}


// smx solvation
    if (rem_read(REM_SMX_SOLVATION) >= 1) {
      smx(jFAv, jFBv);
      if (IteSCF == 1)
	FileMan(FM_WRITE,FILE_SOLVATION_ENERGY_COMPONENTS,FM_DP,1,0,FM_BEG,&ETot);
    }
    else if (rem_read(REM_SMD_PCM) == 1) {
      if (IteSCF == 1)
	FileMan(FM_WRITE,FILE_SOLVATION_ENERGY_COMPONENTS,FM_DP,1,0,FM_BEG,&ETot);
    }


    QTimerOff(t2,tdE);  /* Time the SCF */
    tdC = QTimerOn();

    if (DecompJ) ECou = ENuclear + EV + EJ;  //AML,RDA

    //  Retain unused part of Benny's chemsol implementation
    //  if (rem_read(REM_CHEMSOL) == 1 && IteSCF >= CSStart
    //                                 && (IteSCF-CSStart)%CSPeriod==0 ) {
    //    double* Carts;
    //    INTEGER NAtoms;
    //    get_carts(&Carts,NULL,NULL,&NAtoms);
    //    MakeNN(&ENuclear,Carts,NAtoms,0,0);
    //     Add nuclear-solvent interaction
    //    printf("*** New nuclear energy = %f ***\n",ENuclear);
    //  }

    //if (rem_read(REM_AML_DEBUG) == 45){
#ifdef JKN
    printf("\n");
    if(rem_read(REM_TAO_DFT)>0){
    printf(" Minus  Theta * Entropy = %16.10f\n",EtsA + EtsB);}
    printf(" One-Electron    Energy = %16.10f\n",E1);
    printf(" Total Coulomb   Energy = %16.10f\n",EJ);
    printf(" Alpha Exchange  Energy = %16.10f\n",EKA);
    printf(" Beta  Exchange  Energy = %16.10f\n",EKB );
    printf(" DFT   Exchange  Energy = %16.10f\n",EX );
    printf(" DFT Correlation Energy = %16.10f\n",EC  );
    printf(" Nuclear Attr.   Energy = %16.10f\n",ENuclear);
    if(isXPol)
       printf(" XPOL Nuc-Mull   Energy = %16.12f\n",xpNucMull);
    E_pot += (EJ + EKA + EKB + ENuclear);
    printf("\n Virial Ratio -<V>/<T>:");
    if (XCFunc.HasDFT()){
      printf("\n");
      E_pot += (EX + EC);
      printf("   with correlation term Ec:     %16.10f\n",-(E_pot/E_kin));
      E_pot -= EC;
      printf("   without correlation term Ec:  %16.10f\n\n",-(E_pot/E_kin));
    }else{
      printf("   %16.10f\n\n",-(E_pot/E_kin));
    }
#else
    if (BuildFock){
      if (IPrint >= 1) {
        if(rem_read(REM_TAO_DFT)>0){
            printf(" Minus  Theta * Entropy = %16.10f\n",EtsA + EtsB);}
            printf(" One-Electron    Energy = %16.10f\n",E1);
            printf(" Total Coulomb   Energy = %16.10f\n",EJ);
            printf(" Alpha Exchange  Energy = %16.10f\n",EKA);
            printf(" Beta  Exchange  Energy = %16.10f\n",EKB );
            printf(" DFT   Exchange  Energy = %16.10f\n",EX );
            printf(" DFT Correlation Energy = %16.10f\n",EC  );
            printf(" Kinetic         Energy = %16.10f\n",E1-EV);
            printf(" Nuclear Repu.   Energy = %16.10f\n",ENuclear);
            printf(" Nuclear Attr.   Energy = %16.10f\n",EV);
            printf(" Ewald QM/MM     Energy = %16.10f\n",EewQMMM);
       }
    }
#endif

    // TT store the ground state wave function
    if (rem_read(REM_ROKS)>0){
      if (IteSCF==1)
        VRcopy(jC0,jCAXC,NBas6D*NOrb);
      else
        roks_overlap(jC0,jCAXC);
    }

    /* Complete the formation of the Fock matrices */

    if ((BuildFock && XCFunc.HasDFT() && !rem_read(REM_ROKS)) &&
       ((!dc_dft && !dscf_eda) || (dc_dft && have_hfdens) || (dscf_eda && have_hfdens))) 
    {
      // Adding in XC contribution to square fock matrix
      VRadd(jFAv,jFAv,jXCAv,NB2);
      if (NDen == 2) VRadd(jFBv,jFBv,jXCBv,NB2);
    }

    QTimerOff(Time4Build,Timer4Build);
#ifdef DEVELOPMENT
    printf("Fock build time:  %.2f s (CPU) %.2f s (wall)\n",
	   Time4Build[0],Time4Build[2]);
#endif
    BuildTime += Time4Build[0];

    /* By now we're forced to make square copies of the Fock matrices */

    /* If this is a pure DFT calculation, this is the first point at
       which we're forced to allocate square F's */

    if (BuildFock){
      if ( XCFunc.IsPureDFT() && !(add_LRK || LRC) && ((!dc_dft && !dscf_eda) || (dc_dft && have_hfdens) || 
          (dscf_eda && have_hfdens)) ) 
      {
         jFA = QAllocDouble(N2*NDen);
         jFB = jFA + N2*(NDen-1);
         ScaV2M(jFA,jFAv,True,True);
         if (NDen == 2) ScaV2M(jFB,jFBv,True,True);
         if (rem_read(REM_ROKS)>0) { // ROKS: pure DFT case
           ScaV2M(jPA,jPAv,True,True);
           INTEGER IGrdDF_2 = pick_grid(rem_read(REM_IGRDTY),EMax,IteSCF,NBasis);
           roks_build(jFA,jPA,&E1,&EV,&EJ,&EKA,&EKB,&EX,&EC,jXCAv,jXCBv,
                      jPAv,jCAXC,XCFunc,IGrdDF_2,IPrint,IteSCF,EMax,roks_a,roks_b,ISCF);
           ETot = ENuclear+eNucSolvnt_old+eSolvnt_old+E1+EJ+EKA+EKB+EX+EC+E_EFP+ESolv+E_born+Edisp + Eairbed;
         }
       }
       else {  // For jobs containing K, we can reuse that space for F
         jFA = jKA;
         jFB = jKB;

         if (XCFunc.HasHF() && LRC && rem_read(REM_COMBINE_K) != 1 && !ri_comb_k){
            VRadd(jFA,jFA,jKAsr,N2);
            if (NDen == 2) VRadd(jFB,jFB,jKBsr,N2);
         }

         //printf("scfman: Calling AddV2M\n");
         //      AddV2M(jFA,jFAv,True);
         //      if (NDen == 2) AddV2M(jFB,jFBv,True);

         /* Sort of... here's some temporary code which saves one square
	    matrix for restricted until AddV2M is made to work */

         double* tempF;
         LOGICAL UseMega = meglen() >= N2;
         if (UseMega)
	   tempF = qalloc_double(N2);
         else
	   tempF = QAllocDouble(N2);
         ScaV2M(tempF,jFAv,True,True);
         if (rem_read(REM_ROKS)>0)
           VRcopy(jFA,tempF,N2); // We can use space in jKA for jFA, but we need to toss out the
                                 // old contents of jKA --- if ROKS, we haven't computed jKA yet
         else
           VRadd(jFA,jFA,tempF,N2);
         if (NDen == 2) {
	   ScaV2M(tempF,jFBv,True,True);
	   VRadd(jFB,jFB,tempF,N2);
         }
         if (rem_read(REM_ROKS)>0) { // ROKS: HF and Hybrid DFT cases
           INTEGER IGrdDF_2 = pick_grid(rem_read(REM_IGRDTY),EMax,IteSCF,NBasis);
           roks_build(jFA,jPA,&E1,&EV,&EJ,&EKA,&EKB,&EX,&EC,jXCAv,jXCBv,
                               jPAv,jCAXC,XCFunc,IGrdDF_2,IPrint,IteSCF,EMax,roks_a,roks_b,ISCF);
           ETot = ENuclear+eNucSolvnt_old+eSolvnt_old+E1+EJ+EKA+EKB+EX+EC+E_EFP+ESolv+E_born+Edisp+Eairbed;
         }
         if (UseMega)
	   qfree(tempF);
         else
  	   QFree(tempF);
       }

//PRAGER FDE-Man import and add embedding potential to Fock Matrix

      bool ADC_FDE = (rem_read(REM_FDE));
      bool ADC_FDE_finish = (rem_read(REM_FDE_FINISH));
      int ADC_FDE_prepol = (rem_read(REM_FDE_PREPOL));
      if (ADC_FDE){
    	  double* jPA = QAllocDoubleWithInit(N2);
	  if (use_Pv){ // DFT uses vectorized form
	        // Make it dense
    	    ScaV2M(jPA,jPAv,True,True);
    		FileMan(FM_WRITE,FILE_DENSITY_MATRIX,FM_DP,N2,0,FM_BEG,jPA);
	  }
	  if (ADC_FDE_finish) {
		cout << " Using embedding potential from FDE-Man" << endl;

		double* jFxc = QAllocDoubleWithInit(N2);
		double* jFt = QAllocDoubleWithInit(N2);
		double* jJ = QAllocDoubleWithInit(N2);
		double* jV = QAllocDoubleWithInit(N2);
		double* jv_tot = QAllocDoubleWithInit(N2);

		double E_elstat = 0.0;
		double E_nonel = 0.0;
		double E_J = 0.0;
		double E_V = 0.0;
		double E_xc = 0.0;
		double E_ts = 0.0;
		double E_embed = 0.0;

		FileMan(FM_READ,FILE_FDE_COULOMB_POTENTIAL,FM_DP,N2,0,FM_BEG,jJ);
		FileMan(FM_READ,FILE_FDE_NUC_POTENTIAL,FM_DP,N2,0,FM_BEG,jV);
        if (!rem_read(REM_FDE_ELST)){
		    FileMan(FM_READ,FILE_FDE_T_POTENTIAL,FM_DP,N2,0,FM_BEG,jFt);
		    FileMan(FM_READ,FILE_FDE_XC_POTENTIAL,FM_DP,N2,0,FM_BEG,jFxc);
        }

		// Read DM from file, again?
    		FileMan(FM_READ,FILE_DENSITY_MATRIX,FM_DP,N2,0,FM_BEG,jPA);
		int details = (rem_read(REM_FDE_DETAILS));
		if (details >= 1){
		        double* jv_elstat = QAllocDoubleWithInit(N2);
		        double* jv_nonel = QAllocDoubleWithInit(N2);
		        if (details >= 2){
		      	  VRdot(&E_J,jPA,jJ,N2);
		      	  cout << " Integrated coulomb potential: " << E_J << endl;
		      	  VRdot(&E_V,jPA,jV,N2);
		      		  cout << " Integrated nuclear potential: " << E_V << endl;
		        }
		        VRadd(jv_elstat,jV,jJ,N2);
		        VRdot(&E_elstat,jPA,jv_elstat,N2);
		        cout << " Integrated electrostatic embedding potential: " << E_elstat << endl;
		        if (details >= 2){
		      	  VRdot(&E_xc,jPA,jFxc,N2);
		      		  cout << " Integrated non-add. XC potential: " << E_xc << endl;
		      		  VRdot(&E_ts,jPA,jFt,N2);
		      		  cout << " Integrated non-add. kinetic potential: " << E_ts << endl;
		        }
		        VRadd(jv_nonel,jFxc,jFt,N2);
		        VRdot(&E_nonel,jPA,jv_nonel,N2);
		      	  cout << " Integrated non-electrostatic embedding potential: " << E_nonel << endl;
		      	  QFree(jv_elstat);
		      	  QFree(jv_nonel);
		}
		VRadd(jv_tot,jv_tot,jFt,N2);
		VRadd(jv_tot,jv_tot,jFxc,N2);
		VRadd(jv_tot,jv_tot,jJ,N2);
		VRadd(jv_tot,jv_tot,jV,N2);
		VRdot(&E_embed,jPA,jv_tot,N2);
		cout << " Integrated total embedding potential: " << E_embed << endl;
		/* AZech: I would comment this out, otherwise expectation value of the emb. pot. is double counted
		ETot += E_embed;  //Testen, ob diese Zeile korrekt ist
		        */
		VRadd(jFA,jv_tot,N2);

    		QFree(jV);
    		QFree(jJ);
    		QFree(jFt);
    		QFree(jFxc);
    		QFree(jv_tot);
    	  }
    	  if (ADC_FDE_prepol == 1) {
    		cout << " Using prepolarization of B" << endl;

		double* jJ = QAllocDoubleWithInit(N2);
		double* jV = QAllocDoubleWithInit(N2);
		double* jv_tot = QAllocDoubleWithInit(N2);

		double E_elstat = 0.0;
		double E_J = 0.0;
		double E_V = 0.0;
		double E_embed = 0.0;

		FileMan(FM_READ,FILE_FDE_COULOMB_POTENTIAL,FM_DP,N2,0,FM_BEG,jJ);
		// offset = 0 due to pol_active = True
		FileMan(FM_READ,FILE_FDE_NUC_POTENTIAL,FM_DP,N2,0,FM_BEG,jV);

		// Read DM from file
    		FileMan(FM_READ,FILE_DENSITY_MATRIX,FM_DP,N2,0,FM_BEG,jPA);
		int details = (rem_read(REM_FDE_DETAILS));
		if (details >= 1){
		        double* jv_elstat = QAllocDoubleWithInit(N2);
		        if (details >= 2){
		      	  VRdot(&E_J,jPA,jJ,N2);
		      	  cout << " Coulomb embedding potential energy: " << E_J << endl;
		      	  VRdot(&E_V,jPA,jV,N2);
		      	  cout << " Nuclear embedding potential energy: " << E_V << endl;
		        }
		        VRadd(jv_elstat,jV,jJ,N2);
		        VRdot(&E_elstat,jPA,jv_elstat,N2);
		        cout << " Electrostatic embedding potential energy: " << E_elstat << endl;
		        QFree(jv_elstat);
		}
		VRadd(jv_tot,jv_tot,jJ,N2);
		VRadd(jv_tot,jv_tot,jV,N2);
		VRdot(&E_embed,jPA,jv_tot,N2);
		cout << " Total embedding potential energy for prepolarization of B: " << E_embed << endl;
		/* AZech: I would comment this out, otherwise expectation value of the emb. pot. is double counted
		ETot += E_embed;  //Testen, ob diese Zeile korrekt ist
		*/

		VRadd(jFA,jv_tot,N2);

		QFree(jV);
		QFree(jJ);
		QFree(jv_tot);
    	  }

	  if (ADC_FDE_prepol == 2) {
    	  	cout << " Using prepolarization of B" << endl;

	        double* jVmull = QAllocDoubleWithInit(N2);

	        double E_Vmull = 0.0;

	        FileMan(FM_READ,FILE_MULLIKEN_CHARGES,FM_DP,N2,0,FM_BEG,jVmull);

		// Read DM from file
    		FileMan(FM_READ,FILE_DENSITY_MATRIX,FM_DP,N2,0,FM_BEG,jPA);
	        VRdot(&E_Vmull,jPA,jVmull,N2);
	        cout << " Total embedding potential energy for prepolarization of B: " << E_Vmull << endl;
	        //ETot += E_Vmull;  //Testen, ob diese Zeile korrekt ist

	        VRadd(jFA,jVmull,N2);

	        QFree(jVmull);

	  }

      }

// End FDE-ADC


       // dual basis
       // RST: if needed save Fock for LP correction
       if ((rem_read(REM_SMALL_BASIS_LARGE_BASIS) == 1 && rem_read(REM_DUAL_BASIS_ENERGY) == 1)
             || LPNeedsOld ) {
         jFold = QAllocDouble(N2*NDen);
         VRcopy(jFold,jFA,NBasis*NBasis);
         if (NDen == 2) VRcopy(jFold+N2,jFB,NBasis*NBasis);
       }

    }  /* Really, truly finished with Fock build */

    else{
       // If we skipped the Fock build, some allocations may be in order
       if ( XCFunc.IsPureDFT() && !(add_LRK || LRC) && !ri_comb_k && ((!dc_dft && !dscf_eda) || 
          (dc_dft && have_hfdens) || (dscf_eda && have_hfdens)) ) 
       {
          jFA = QAllocDouble(N2*NDen);
          jFB = jFA + N2*(NDen-1);
       }
       else {
          jFA=jKA; jFB=jKB;
          if (XCFunc.HasHF() && LRC){
             VRadd(jFA,jFA,jKAsr,N2);
             if (NDen == 2) VRadd(jFB,jFB,jKBsr,N2);
          }
       }

       FileMan_Open_Read(FILE_EXTRAP_FOCK_MATRIX);
       FileMan(FM_READ,FILE_FOCK_MATRIX,FM_DP,N*N,0,FM_BEG,jFA);
       if (Unrestricted)
          FileMan(FM_READ,FILE_FOCK_MATRIX,FM_DP,N*N,0,FM_CUR,jFB);
       FileMan_Close(FILE_EXTRAP_FOCK_MATRIX);
    }
//AJWT - This seems to have finally finished with the Normal Fock Build.  SCF_MINFIND and SCF_SAVEMINIMA and SCF_READMINIMA modify the fock matrix now
//       jFA and jFB contain alpha and beta square (not vectorized) Fock matrices.  If we're doing RHF, then these point to the same memory.
// /AJWT


//AJWT check to see if we've fallen into a minimum well for SCF_SAVEMINIMA
    mf.Penalize(jFA,jFB,jPA,jPB,EMax,ETot);
// We've finised modifying the Fock matrix to add penalty functions.
// /AJWT

//AJWT - The Penalize Fock Build is now over.
//       jFA and jFB contain alpha and beta square (not vectorized) Fock matrices.  If we're doing RHF, then these point to the same memory.
// /AJWT


    //KCF STEP routine
    if( rem_read(REM_STEP) == 1 && rem_read(REM_IGUESS) != SAD && rem_read(REM_IGUESS) != AUTOSAD){
        // need to read coefs here at every iteration
        // this means IGUESS better be READ or FRAGMO or we're dead in the water
        jCA = QAllocDouble(NDen*NOrb*NBasis);
        jCB = jCA + (NDen-1)*NOrb*NBasis;
        FileMan(FM_READ,FILE_MO_COEFS,FM_DP,NDen*NOrb*NBasis,0,FM_BEG,jCA);
        step(jFA,jCA,jS,eta_A,eta_B,NAlpha,NBasis,NOrb,IteSCF,true,true,step_always_alpha);
        if( NDen == 2 )
            step(jFB,jCB,jS,eta_A,eta_B,NBeta,NBasis,NOrb,IteSCF,false,true,step_always_beta);
        // copy fock back over
        ScaV2M(jFA,jFAv,True,False);
        if(NDen == 2) ScaV2M(jFB,jFBv,True,False);
        // free the things
        QFree(jCA);
    }
    else if( (rem_read(REM_STEP) == 1 && rem_read(REM_IGUESS) == SAD)
             || (rem_read(REM_STEP) == 1 && rem_read(REM_IGUESS) == AUTOSAD))
        QCrash("STEP requires a set of guess MO coefficients!");

    if (usingGDM || usingDM || NoSCF || usingGDIIS ||usingNEGF) {

      // Save a copy of the latest Fock matrices; they may be needed later
      // for various purposes (getting canonical MOs, Fock fitting...)

      FileMan_Open_Write(FILE_TEMP_FOCK);
      FileMan(FM_WRITE,FILE_TEMP_FOCK,FM_DP,N*N,0,FM_BEG,jFA);
      FileMan(FM_WRITE,FILE_TEMP_FOCK,FM_DP,N*N,0,FM_CUR,jFB);
      FileMan_Close(FILE_TEMP_FOCK);

      if (IPrint >= 2) {
	MatPrint(jFA,N,N,"Alpha Fock Matrix");
	if (NDen == 2) MatPrint(jFB,N,N,"Beta Fock Matrix");
      }
    }

    /* RCL(06/06) For O2 Method */
    LOGICAL DoO2;
    DoO2 = (rem_read(REM_DO_O2) == 1 || rem_read(REM_DO_O2) == 2 || rem_read(REM_DO_O2) == 3) ? 1 : 0;

// A few cautions while doing O2
    if (DoO2){
	if (!canUseGDM)
	  QCrash("Need GDM or DIIS_GDM scf_algorithm for O2 calculation!");
        if (rem_read(REM_LEVCOR) >= 102)
          QCrash("Cannot specify both Do_O2 and CORRELATION keywords");
        if (rem_read(REM_NWINLO) > 0 || rem_read(REM_NWINHI) > 0 )
          QCrash("Frozen core not yet implemented for O2 methodologies");
    }

    if (DoO2 && usingGDM) {

      printf("\n Doing O2 orbital optimization step \n");
      /* Allocate for the MOs and eigenvalues */

      jCA = QAllocDouble(NBasis*NOrb*NMO);
      jCB = jCA + NBasis*NOrb*(NMO-1);
      jEA = QAllocDouble(NOrb*NMO);
      jEB = jEA + NOrb*(NMO-1);

      FileMan(FM_READ,FILE_MO_COEFS,FM_DP,N*NOrb,0,FM_BEG,jCA);
      FileMan(FM_READ,FILE_MO_COEFS,FM_DP,N*NOrb,0,FM_CUR,jCB);
      FileMan(FM_READ,FILE_MO_COEFS,FM_DP,NOrb,  0,FM_CUR,jEA);
      FileMan(FM_READ,FILE_MO_COEFS,FM_DP,NOrb,  0,FM_CUR,jEB);
// write to FILE_O2_DATA
      INTEGER noff = 1 + 2*NOrb*NBasis;
      FileMan(FM_WRITE,FILE_O2_DATA,FM_DP,N*NOrb,noff,FM_BEG,jCA);
      FileMan(FM_WRITE,FILE_O2_DATA,FM_DP,N*NOrb,0,FM_CUR,jCB);
      FileMan(FM_WRITE,FILE_O2_DATA,FM_DP,NOrb,  0,FM_CUR,jEA);
      FileMan(FM_WRITE,FILE_O2_DATA,FM_DP,NOrb,  0,FM_CUR,jEB);

      QFree(jCA);QFree(jEA);

      // Call mosmp2.F to evaluate SOS Energy and L (=dE(OS)/dU)

      INTEGER LenV = megtot();
      if (NBeta == 0 && NAlpha == 1) {
	printf("Only 1 electron, nothing to correlate..skipping correlation\n");
        double Zero = 0.0;
        FileMan(FM_WRITE,FILE_O2_DATA,FM_DP,noff,0,FM_BEG,&Zero);
      }
      else if (rem_read(REM_DO_O2) == 1 || rem_read(REM_DO_O2) == 2)
        mosmp2(qalloc_start(),&LenV);
      else if (rem_read(REM_DO_O2) == 3)
        rimp2grad(qalloc_start());
      //Read SOS from disk Energy and increment ETot
      double ESOS = 0.0;
      FileMan(FM_READ,FILE_O2_DATA,FM_DP,1,0,FM_BEG,&ESOS);
      printf("ETot before SOS = %20.10f\n",ETot);
      ETot += ESOS;
      printf("ETot after SOS = %20.10f\n",ETot);
    } //End DoO2

    /* Construct a (hopefully) better set of MO coefficients by
       various means */

    //RST: time scf
    qtime_t rusty40;
    double rusty41[3];
    rusty40 = QTimerOn();

      //BJA_Corr! muProjOpA Correction to jFA

      if (rem_read(REM_EMBED_INTERNAL)){

         if (IPrint >= 2) {
	       MatPrint(jFA,N,N,"jFA");
           cout << "jFA += mu*jProjOpA" << endl;
         }
         VRscale(jProjOpA, N2, mufact);
         VRadd(jFA, jProjOpA, jFA, N2);
         VRscale(jProjOpA, N2, 1.0 / mufact);
      }

    /* Here comes the messy part as far as memory usage is concerned.
       We are forced to use square matrices for the Fock, density and
       MO coefficient matrices. */

    if (usingGDM || usingDM || usingGDIIS) {  // Fock2MO process using DM

      /* Allocate for the MOs and eigenvalues */

      jCA = QAllocDouble(NBasis*NOrb*NMO);
      jCB = jCA + NBasis*NOrb*(NMO-1);
      jEA = QAllocDouble(NOrb*NMO);
      jEB = jEA + NOrb*(NMO-1);

      if ((dc_dft && have_dftE) || (dscf_eda && have_dftE)) 
      {  //cout << "JMH: DC_FileSave call #1\n";
         DC_FileSave(1,NBasis,NDen,NB2,NOrb,N2,jFA,jFB,jS);
      }

      FileMan(FM_READ,FILE_MO_COEFS,FM_DP,N*NOrb,0,FM_BEG,jCA);
      if (NMO == 2) FileMan(FM_READ,FILE_MO_COEFS,FM_DP,N*NOrb,0,FM_CUR,jCB);
      if (ISCF == 2) VRcopy(jCB,jCA,NBasis*NOrb);

      /* Get square versions of P if we don't already have them */
      if ( XCFunc.IsPureDFT() && !(add_LRK || LRC) && !rem_read(REM_ROKS) &&
         ((!dc_dft && !dscf_eda) || (dc_dft && have_hfdens) || (dscf_eda && have_hfdens)) ) {
	jPA = QAllocDouble(N2*NDen);
	jPB = jPA + N2*(NDen-1);
	FileMan(FM_READ,FILE_DENSITY_MATRIX,FM_DP,N2*NDen,0,FM_BEG,jPA);
      }

      //      GenMatrix FA(jFA,N,N),FB(jFB,N,N),PA(jPA,N,N),PB(jPB,N,N);
      // if (IteSCF > 1) {
      //   INTEGER IVShift = rem_read(REM_VSHIFT);
      //   if (IVShift > 0) {
      //     double VShift = IVShift / 1000.0;
      //     ShiftVirtuals(FA,FB,VShift);
      //   }
      // }

      if (!MP2Restart && !MOMFroz){
         if (ItDM == 0 && usingDM) {
            initdm(jCA,jCB,jPA,jPB,jTh,&EMax,jFA,jFB,&N,&NOrb,&NOA,&NVA,&NOB,&NVB,
	           &NTheta,&ISCF,&IUnRot,&True,qalloc_start());
	    ItDM = 1;
         }
         else if(usingDM) {
	    INTEGER IComment[50],ICommentLen;
	    rotmin(IComment,&ICommentLen,jCA,jCB,jPA,jPB,jTh,jGr,&EMax,&ItDM,
	          jFA,jFB,&ETot,&ISCF,&N,&NOrb,&NOA,&NVA,&NOB,&NVB,&NTheta,
	          &IUnRot,&IUnSSV,&NSSV,qalloc_start());
	    // Decipher comment from FORTRAN code
	    Comment.Decode(IComment,ICommentLen);
         }
         else if(usingGDM) {
	    INTEGER IComment[50],ICommentLen;
	    //getewc(jCA,jCB,jPA,jPB,jTh,&EMax,jFA,jFB,&N,&NOrb,&NOA,&NVA,&NOB,&NVB,
	   //       &NTheta,&ISCF,&IUnRot,&IPseu,&True,qalloc_start());

	   rungdm(IComment,&ICommentLen,jCA,jCB,jTh,jGr,&EMax,&ItDM,
	          jFA,jFB,&ETot,&ISCF,&N,&NOrb,&NOA,&NVA,&NOB,&NVB,&NTheta,
	          &IUnRot,&IPseu,&IUnSSV,&IBFGS,&IEWSS,&NSSV,qalloc_start());
	   ItDM = 1;

	   Comment.Decode(IComment,ICommentLen);
         }

         else if(usingGDIIS) {

	    INTEGER IComment[50],ICommentLen;

	    gdiis(IComment,&ICommentLen,jCA,jCB,jGr,&GRMS,&EMax,&ItDM,&IteSCF,&CurDIIS,&TotDIIS,
	          jFA,jFB,jS,&ETot,&ISCF,&N,&NOrb,&NOA,&NVA,&NOB,&NVB,&NTheta,&Step,&Curv,
	          &EOld0,&IUnRot,&IBFGS,&IEWSS,&ConvOK,qalloc_start());
	    if(EMax*EMax>1.e3){EMax=10.*Cnverg;}

	       Comment.Decode(IComment,ICommentLen);
         }
      }

      // We don't need the square Fock matrices anymore

      QFree(jFA);

    } // end if GDM || DM || bGDIIS
    else if(UseRCA) // We're still in the Fock2MO part
    {
      /* Get square versions of P if we don't already have them */
      if (jPA == NULL) {
	jPA = QAllocDouble(N2*NDen);
	jPB = jPA + N2*(NDen-1);
	FileMan(FM_READ,FILE_DENSITY_MATRIX,FM_DP,N2*NDen,0,FM_BEG,jPA);
      }

      if ((dc_dft && have_dftE) || (dscf_eda && have_dftE)) 
      {  //cout << "JMH: DC_FileSave call #2\n";
         DC_FileSave(1,NBasis,NDen,NB2,NOrb,N2,jFA,jFB,jS);
      }

      //Re-Load one electron H
      jHv = OneEMtrx().getH();

      //Allocate Scratch Space
      double *jT1=NULL, *jT2=NULL, *jT3=NULL, *jT4=NULL;
      jT1 =QAllocDouble(max(N*N,NB2car));
      jT2 =QAllocDouble(max(N*N,NB2car));
      jT3 =QAllocDouble(max(N*N,NB2car));
      jT4 =QAllocDouble(max(N*N,NB2car));

      //Open the Temporary Files
      FileMan_Open_RW(FILE_RCA_DENSITY);
      FileMan_Open_RW(FILE_RCA_FOCK);
      FileMan_Open_RW(FILE_RCA_XC);

      Quad_not_Conv=True;
      for(int ii=0; ii<3 && Quad_not_Conv; ii++){ // Loop to ensure correct DFT xc
	//Call RCA routine
	runrca(jPA,jPB,jFA,jFB,jT1,jT2,jT3,jT4,jHv,&ETot,
	       jxRCA,jARCA,jERCA,jE0RCA,jdxRCA,jgxRCA,
	       &ItRCA,&NDen,&N,&NSS);

	//Correct for non-linearity of XC part of F
	EOld=ETot;
	if (XCFunc.HasDFT()) {
	  //Save Current XC information
	  INTEGER iSS=(ItRCA-1)%NSS+1;
	  ScaV2M(jT1,jXCAv,True,True);
	  if (NDen>1) ScaV2M(jT2,jXCBv,True,True);
	  FileMan(FM_WRITE,FILE_RCA_XC,FM_DP,N*N,(iSS-1)*NDen*N*N,FM_BEG,jT1);
	  if (NDen>1) FileMan(FM_WRITE,FILE_RCA_XC,FM_DP,N*N,
			      ((iSS-1)*NDen+NDen-1)*N*N,FM_BEG,jT2);

	  //Re-Generate Sparse versions of P
	  ScaV2M(jPA,jPAv,True,False);
	  if (NDen == 2) ScaV2M(jPB,jPBv,True,False);
	  // Compute XC component of Fock Matrix
	  IGrdDF_2 = pick_grid(rem_read(REM_IGRDTY),EMax,IteSCF,NBasis);
	  rem_write(pick_XC_thresh(IGrdDF_2!=rem_read(REM_IGRDTY),EMax,Cnverg),
		    REM_DFT_THRESH);
	  //For some reason IncDFT screws this part up....  So turn it off
	  rem_write(1,REM_RESTART_INCDFT);
	  DFTman(&EX,&EC,jXCAv,jXCBv,jPAv,jCAXC,NULL,NULL,2,
		 XCFunc,IGrdDF_2,IPrint-2,IteSCF, EMax);

      //YMao: the following is necessary for RCA to work correctly with
      //      functionals containing NLC
      INTEGER iNLC = rem_read(REM_NL_CORRELATION);
      if (iNLC > 0) {
          double *jNLAv, *jNLBv;
          if (XCFunc.NumExch()>0 || XCFunc.NumCorr()>0)
            jNLAv = QAllocDouble2(NB2car*NDen,shared);
          else jNLAv = jXCAv;
          jNLBv = jNLAv + NB2car*(NDen-1);

          IGrdDF_2 = pick_grid(rem_read(REM_NL_GRID),EMax,IteSCF,NBasis);
          rem_write(pick_XC_thresh(IGrdDF_2!=rem_read(REM_NL_GRID),EMax,Cnverg),
              REM_DFT_THRESH);
          double Junk, ENLC;

          DFTman(&Junk,&ENLC,jNLAv,jNLBv,jPAv,jCAXC,NULL,NULL,1,
              XCFunctional(0,CFUNC_NL_Init),IGrdDF_2,IPrint-2,IteSCF,EMax);
          DFTman(&Junk,&ENLC,jNLAv,jNLBv,jPAv,jCAXC,NULL,NULL,2,
              XCFunctional(0,CFUNC_NL_Eval),IGrdDF_2,IPrint-2,IteSCF, EMax);
          if (XCFunc.NumExch()>0 || XCFunc.NumCorr()>0) {
            VRadd(jXCAv,jXCAv,jNLAv,NB2);
            if (NDen == 2) VRadd(jXCBv,jXCBv,jNLBv,NB2);
            QFree(jNLAv);
            EC += ENLC;
          }
          else EC = ENLC;
     }

	 EXC=EX+EC;

	 //Update Current Fock Matrix and Energy with New XC part
#ifdef DEVELOPMENT
	 cout << "ETot = " << ETot << ", Before updatexc " <<  endl;
#endif
	 updatexc(jxRCA,&EXC,jXCAv,jXCBv,jFA,jFB,jPA,jPB,jT1,jT2,jHv,
		   &ETot,&N,&NSS,&ItRCA,&NDen);
	}
	//If the predicted Energy is anywhere close, move on:
	if(ItRCA>1) {
	  INTEGER jSS=(ItRCA-2)%NSS;
	  if( (jERCA[jSS]-ETot) > .1*(jERCA[jSS]-EOld)){
	    Quad_not_Conv=False;
	  }else{
	    printf("Recomputing EXC %f %f %f \n",ETot,EOld,jERCA[jSS]);
	  }
	} else {
	  Quad_not_Conv=False;
        }
        // On Last Iteration, throw out previous data if not converged
        if (ii == 2 && Quad_not_Conv)
          ItRCA = 1;
      }
      //Update RCA subspace info
      getss(jARCA,jPA,jPB,jFA,jFB,jERCA,jE0RCA,&ETot,jT1,jT2,jT3,jT4,jHv,
	    &N,&NSS,&ItRCA,&NDen);

      //Close Temporary Files
      FileMan_Close(FILE_RCA_DENSITY);
      FileMan_Close(FILE_RCA_FOCK);
      FileMan_Close(FILE_RCA_XC);

      //Don't start counting on first iteration of (non-idempotent) SAD Guess
      //    or if it's the first iteration with C-DFT
      if (!(IteSCF == 1 && rem_read(REM_IGUESS) == SAD) &&
          !(IteSCF == 1 && rem_read(REM_CDFT))) ItRCA=ItRCA+1;

      // Update DIIS Information (without accepting the DIIS step)
      VRcopy(jT1,jFA,N*N); VRcopy(jT2,jFB,N*N);
      VRcopy(jT3,jPA,N*N); VRcopy(jT4,jPB,N*N);
      GenMatrix T1(jT1,N,N),T2(jT2,N,N),T3(jT3,N,N),T4(jT4,N,N);

      //@@TAV : Fix DIIS initialization ?

      if (!rem_read(REM_CDFT))
        diisControl.NextCycle(T1,T2,T3,T4);
      else {// We're doing CDFT
        bool LambdaMode = rem_read(REM_CDFT_LAMBDA_MODE);
        int nmat = rem_read(REM_CDFT);
        if (jCDFT == NULL){     // Initialization
          jCDFT = new cdft_data(nmat,NDen,NBasis);
          cdft_init(jCDFT,
                    jPAv, IPrint, IteSCF, NBasis, Cnverg, EMax,
                    NDen, NB2car);
          if (LambdaMode)
            VRcopy(jCDFT->Lams,jCDFT->Vals,nmat);
        }
        GenMatrix T1_0(N,N), T2_0(N,N);
        T1_0.Set(T1); T2_0.Set(T2);

        if (LambdaMode)
          cdft_lam2fock(jT1, jT2, jCDFT, nmat, NDen, NBasis);
        else
          cdft_converged = cdft_rootsearch(jT1, jT2, jCDFT, NAlpha, NBeta, NDen, NOrb, NBasis, EMax);

        VRcopy(jFA,jT1,N*N); if (NDen == 2) VRcopy(jFB,jT2,N*N);
        diisControl.NextCycle_cdft(T1,T2,T1_0,T2_0,T3,T4);
      }

      EMax = diisControl.CurrentError();
      if ((IteSCF == 1 && rem_read(REM_IGUESS) == SAD) ||
          (IteSCF == 1 && rem_read(REM_CDFT))) diisControl.Reset(0);
      QFree(jT1);
      QFree(jT2);
      QFree(jT3);
      QFree(jT4);

      //Obtain New MOs from Fock Matrix and save current F
      if (jCA == NULL) {
	jCA = QAllocDouble(NBasis*NOrb*NMO);
	jCB = jCA + NBasis*NOrb*(NMO-1);
      }
      if (jEA == NULL){
	jEA = QAllocDouble(NOrb*NMO);
	jEB = jEA + NOrb*(NMO-1);
      }

      if ((!dc_dft && !dscf_eda) || (dc_dft && !have_dftE) || (dscf_eda && !have_dftE)){
         FileMan_Open_Write(FILE_TEMP_FOCK);
         FileMan(FM_WRITE,FILE_TEMP_FOCK,FM_DP,N*N,0,FM_BEG,jFA);
         FileMan(FM_WRITE,FILE_TEMP_FOCK,FM_DP,N*N,0,FM_CUR,jFB);
         FileMan_Close(FILE_TEMP_FOCK);
      }

      if (rem_read(REM_CDFTCI_FRAGMENT)>0) {
	Fock2MOBlockCDFTCI(jCA,jEA,jFA,NAlpha,1);
	if (NMO == 2) Fock2MOBlockCDFTCI(jCB,jEB,jFB,NBeta,2);
      } else {
        Fock2MO(jCA,jEA,jFA);
        if (NMO == 2) Fock2MO(jCB,jEB,jFB);
      }

      // We don't need the square Fock matrices anymore
      QFree(jFA);


    } // end if UseRCA
    else if(usingNEGF) { //--- Here main part of NEGF ---
      /* The G^< (density) will be calculated using the current set of
       *          the fock matrices to generate a new density
       *                */
      tdnegf = QTimerOn();
      if(IteSCF==1) printf("Inside NEGF loop\n");

      if ((dc_dft && have_dftE) || (dscf_eda && have_dftE)) 
      {  //cout << "JMH: DC_FileSave call #3\n";
         DC_FileSave(1,NBasis,NDen,NB2,NOrb,N2,jFA,jFB,jS);
      }


      //if (XCFunc.IsPureDFT() && (!dc_dft || (dc_dft && have_hfdens)))
      if (XCFunc.IsPureDFT() && ((!dc_dft && !dscf_eda) || (dc_dft && have_hfdens) || (dscf_eda && have_hfdens))) 
      {
	jPA = QAllocDouble(N2*NDen);
	jPB = jPA + N2*(NDen-1);
	FileMan(FM_READ,FILE_DENSITY_MATRIX,FM_DP,N2*NDen,0,FM_BEG,jPA);
      }
      jCA = QAllocDouble(NBasis*NOrb*NMO);
      jCB = jCA + NBasis*NOrb*(NMO-1);
      jEA = QAllocDouble(NOrb*NMO);
      jEB = jEA + NOrb*(NMO-1);


      // Calculated orbital energy (before modifying Fock matrix) and save some needed orbital energies
      double *tmp_jFA=NULL,*tmp_jFB=NULL;
      if(IteSCF==1){
	tmp_jFA = QAllocDouble(N2*NDen);
	tmp_jFB = tmp_jFA + N2*(NDen-1);
                   for(i=0; i<N2; i++) tmp_jFA[i]= jFA[i];
        if(NMO==2) for(i=0; i<N2; i++) tmp_jFB[i]= jFB[i];
                   Fock2MO( jCA,jEA,tmp_jFA );
        if(NMO==2) Fock2MO( jCB,jEB,tmp_jFB );
        rw_disc_trans_6_double(&jEA[0],&jEB[0],&jEA[NAlpha-1],&jEB[NBeta-1],&jEA[NAlpha],&jEB[NBeta],"NEGF_comm1.tmp","save");
	QFree(tmp_jFA);

	            printf("(Before modification of Fock matrix)  \n");
	            printf("   Homo & Lumo:  %9.4f  %9.4f (alpha)\n",jEA[NAlpha-1],jEA[NAlpha]);
         if(NMO==2) printf("                 %9.4f  %9.4f (beta) \n",jEB[NBeta-1], jEB[NBeta] );
	            printf("   Lowest orbital level:  %12.3f  (alpha)\n",jEA[0]);
         if(NMO==2) printf("                          %12.3f  (beta) \n",jEB[0]);
      }

      // Modify Fock matrix:  h(Hcore) and J matrices with readinESP, readinHS,
      // and add bias voltage by solving Poisson equation with boundary condition
      //printf("XXX skip modify_fock_negf XXX\n");
      modify_fock_negf(NBasis,NOrb,NMO,NDen,jPA,jPB,jFA,jFB,jS,IteSCF);


      // Calculated orbital energy based on modified Fock matrix and save some needed orbital energies
      tmp_jFA = QAllocDouble(N2*NDen);
      tmp_jFB = tmp_jFA + N2*(NDen-1);
                 for(i=0; i<N2; i++) tmp_jFA[i]= jFA[i];
      if(NMO==2) for(i=0; i<N2; i++) tmp_jFB[i]= jFB[i];
                 Fock2MO( jCA,jEA,tmp_jFA );
      if(NMO==2) Fock2MO( jCB,jEB,tmp_jFB );
      rw_disc_trans_6_double(&jEA[0],&jEB[0],&jEA[NAlpha-1],&jEB[NBeta-1],&jEA[NAlpha],&jEB[NBeta],"NEGF_comm1.tmp","save");
      QFree(tmp_jFA);


      // Print the frontier orbital energy at IteSCF=1
      if(IteSCF==1) {
	            printf("(After modification of Fock matrix)  \n");
	            printf("   Homo & Lumo (modified Fock matrix):  %9.4f  %9.4f (alpha)\n",jEA[NAlpha-1],jEA[NAlpha]);
         if(NMO==2) printf("                                        %9.4f  %9.4f (beta) \n",jEB[NBeta-1], jEB[NBeta] );
	            printf("   Lowest orbital level (modified Fock matrix):  %12.3f  (alpha)\n",jEA[0]);
         if(NMO==2) printf("                                                 %12.3f  (beta) \n",jEB[0]);
      }

      if(IteSCF==1) printf("(From here, first update of density matrix)  \n");

      // Update Density matrix except for central block from the modified Fock matrix
      if(tran_opt==3) {
	 int  flg_updateDmatLR;
 	 flg_updateDmatLR = rem_read(REM_TRANS_UPDATEDMATLR);
	 if( flg_updateDmatLR != 0 ) {
	    double *tmp_jPA=NULL,*tmp_jPB=NULL;
	    tmp_jPA = QAllocDouble(N2*NDen);
	    tmp_jPB = tmp_jPA + N2*(NDen-1);
                       MO2Den(tmp_jPA,jCA,N,1,NAlpha);
            if(NMO==2) MO2Den(tmp_jPB,jCB,N,1,NBeta);
	    update_DmatLR( N,NMO,jPA,jPB,tmp_jPA,tmp_jPB,IteSCF,flg_updateDmatLR );
  	               FileMan(FM_WRITE,FILE_DENSITY_MATRIX,1,N2,0,1,jPA);
            if(NMO==2) FileMan(FM_WRITE,FILE_DENSITY_MATRIX,1,N2,0,2,jPB);
	    QFree(tmp_jPA);
	 }
      }


      //(Go to calculation of NEGF core part -- Update Density Matrix)
      int Analysis=0, PrintLevel=0;
      if(IteSCF==1) PrintLevel=1;
      transcpp_main(NBasis,NOrb,NMO,NDen,jFA,jFB,jPA,jPB,jS,IteSCF,PrintLevel,Analysis);

      //print_transmission_tdos(NBasis,NOrb,NMO,NDen,IteSCF,&iVbias,jFA,jFB,jPA,jPB,jS,"XXX");

                 FileMan(FM_READ,FILE_MO_COEFS,FM_DP,N*NOrb,0,FM_BEG,jCA);
      if(NMO==2) FileMan(FM_READ,FILE_MO_COEFS,FM_DP,N*NOrb,0,FM_CUR,jCB);


      //(Judge Convergence)
      if( IteSCF >= 1 ) {
	 double maxdif;
	 rw_disc_trans_1D_double(&maxdif,1,"NEGF_maxdif.tmp","load");
	 if (maxdif <= Cnverg_NEGF) Converged = TRUE;
	 else                       Converged = FALSE;

	 if(Converged){

	   if(tran_opt==4){
	      //(Print F, S, D matrix on file at the voltage)
 	                 FileMan(FM_READ,FILE_DENSITY_MATRIX,FM_DP,N2,0,FM_BEG,jPA);
	      if(NMO==2) FileMan(FM_READ,FILE_DENSITY_MATRIX,FM_DP,N2,0,FM_CUR,jPB);
	      rw_disc_trans_FSDmat( NBasis,NMO,jFA,jFB,jPA,jPB,jS,&iVbias,Converged,"save" );

	      //(Print T(E),TDOS,Current on file at the voltage)
	      //print_transmission_tdos(NBasis,NOrb,NMO,NDen,IteSCF,&iVbias,jFA,jFB,jPA,jPB,jS,"Conv");
	      print_transmission_tdos(NBasis,NOrb,NMO,NDen,IteSCF,&iVbias,jFA,jFB,jPA,jPB,jS,"NoExName");

	      files_NEGF_after_conv(NMO,iVbias);
	   }

	   FileMan_Open_Write(FILE_TEMP_FOCK);
	   FileMan(FM_WRITE,FILE_TEMP_FOCK,FM_DP,N*N,0,FM_BEG,jFA);
	   FileMan(FM_WRITE,FILE_TEMP_FOCK,FM_DP,N*N,0,FM_CUR,jFB);
	   FileMan_Close(FILE_TEMP_FOCK);

	   //(coefficient must be from density matrix, not from Fock matrix)
	   double *tmp_jCA=NULL,*tmp_jCB=NULL;
	   tmp_jCA = QAllocDouble(NBasis*NOrb*NMO);
	   tmp_jCB = tmp_jCA + NBasis*NOrb*(NMO-1);
	              Fock2MO( tmp_jCA,jEA,jFA );
           if(NMO==2) Fock2MO( tmp_jCB,jEB,jFB );
	   QFree(tmp_jCA);

	   FileMan(FM_WRITE,FILE_MO_COEFS,FM_DP,N*NOrb,0,FM_BEG,jCA);
	   FileMan(FM_WRITE,FILE_MO_COEFS,FM_DP,N*NOrb,0,FM_CUR,jCB);
	   FileMan(FM_WRITE,FILE_MO_COEFS,FM_DP,NOrb,  0,FM_CUR,jEA);
	   FileMan(FM_WRITE,FILE_MO_COEFS,FM_DP,NOrb,  0,FM_CUR,jEB);
	 }

      } //(end of judge convergence)
      if(!Converged && IteSCF==MaxSCF){
  	   printf("  #-----------------------------------------------\n");
  	   printf("   %d NEGF did not converge. Matrices are printed.\n",IteSCF);
 	              FileMan(FM_READ,FILE_DENSITY_MATRIX,FM_DP,N2,0,FM_BEG,jPA);
	   if(NMO==2) FileMan(FM_READ,FILE_DENSITY_MATRIX,FM_DP,N2,0,FM_CUR,jPB);
	   rw_disc_trans_FSDmat( NBasis,NMO,jFA,jFB,jPA,jPB,jS,&iVbias,Converged,"save" );
      }


      QFree(jFA);

      if(IteSCF==1) printf("\nNEGF initial step done\n");
      printf("   #- - - - - - - - - - - - - - - - - - - - - - -\n");
      QTimerOff(t3,tdnegf);
      if(rem_read(REM_PRINT_SCF_TIME)>0) printf("  time: NEGF CPU %.2f s  wall %.2f s\n",t3[0],t3[2]);

    } // end of NEGF
    //**********************************************************************//

    else // Still in Fock2MO mode
    {  // We're doing DIIS extrapolation

      /* Get square versions of P if we don't already have them.
	 These are needed for computing the DIIS error vector. */

      if ( XCFunc.IsPureDFT() && !(add_LRK || LRC) && ((!dc_dft && !dscf_eda) || (dc_dft && have_hfdens) ||  
          (dscf_eda && have_hfdens)) ) 
      {
	jPA = QAllocDouble(N2*NDen);
	jPB = jPA + N2*(NDen-1);
	FileMan(FM_READ,FILE_DENSITY_MATRIX,FM_DP,N2*NDen,0,FM_BEG,jPA);
      }
      if ((dc_dft && have_dftE) || (dscf_eda && have_dftE)) 
      {  //cout << "JMH: DC_FileSave call #4\n";
         DC_FileSave(1,NBasis,NDen,NB2,NOrb,N2,jFA,jFB,jS);
      }
      if (IPrint >= 2) {
	MatPrint(jFA,N,N,"Calculated Alpha Fock Matrix");
	if (NDen == 2) MatPrint(jFB,N,N,"Calculated Beta Fock Matrix");
      }
/*
      // Save Fock matrix to perform EDA for FRZ and POL terms later
      double *jF_EDA_copy=NULL;
      if (rem_read(REM_DO_E_DECOMP)>0 && LPSCFMI>0) {
        jF_EDA_copy=QAllocDouble(N2*NDen);
        VRcopy(jF_EDA_copy,jFA,N2);
        if (NDen==2) VRcopy(jF_EDA_copy+N2,jFB,N2);
      }
*/
      threading_policy::enable_blas_only();
      tdf2m = QTimerOn();

      GenMatrix FA(jFA,N,N),FB(jFB,N,N),PA(jPA,N,N),PB(jPB,N,N);
      // !!! Should be more sophisticated about when VShift is turned on
      // if (IteSCF > 1) {
      //   INTEGER IVShift = rem_read(REM_VSHIFT);
      //   if (IVShift > 0) {
      //     double VShift = IVShift / 1000.0;
      //     ShiftVirtuals(FA,FB,VShift);
      //   }
      // }
      if (CyclicSampling){
        DIIScs.NextCycle(FA,FB,PA,PB);
        EMax = DIIScs.CurrentError();
      }else if (rem_read(REM_CDFT)){ // CDFT
        int nmat = rem_read(REM_CDFT);
        bool DoPreDIIS = rem_read(REM_CDFT_PREDIIS);
        bool DoPostDIIS = rem_read(REM_CDFT_POSTDIIS);
        bool LambdaMode = rem_read(REM_CDFT_LAMBDA_MODE);
        GenMatrix FA0(N,N), FB0(N,N);
        FA0.Set(FA); if (NDen==2) FB0.Set(FB);

        if (jCDFT == NULL){     // Initialization
          jCDFT = new cdft_data(nmat,NDen,NBasis);
          cdft_init(jCDFT,
                    jPAv, IPrint, IteSCF, NBasis, Cnverg, EMax,
                    NDen, NB2car);
          DoPreDIIS = true;

          if (LambdaMode)
            VRcopy(jCDFT->Lams,jCDFT->Vals,nmat);
        }

        if (LambdaMode){ DoPreDIIS = false; DoPostDIIS = false; }

        if (DoPreDIIS)
          cdft_converged = cdft_rootsearch(jFA, jFB, jCDFT, NAlpha, NBeta, NDen, NOrb, NBasis, EMax);
        else
          cdft_lam2fock(jFA, jFB, jCDFT, nmat, NDen, NBasis);

        diisControl.NextCycle_cdft(FA,FB,FA0,FB0,PA,PB);
        EMax = diisControl.CurrentError();

        if (DoPostDIIS){
          FA.Set(FA0); if (NDen==2) FB.Set(FB0);
          cdft_converged = cdft_rootsearch(jFA, jFB, jCDFT, NAlpha, NBeta, NDen, NOrb, NBasis, EMax);
        }
	// XXX BJK we leak FA0 and FB0?!

      }
      else if (rem_read(REM_ROKS) > 0) {
        //double *jFC, *jPC;
        jFC = QAllocDouble(NBas6D*NBas6D);
        jPC = QAllocDouble(NBas6D*NBas6D);
        VRcopy(jFC,jFA,N2);
        VRcopy(jPC,jPA,N2);
        GenMatrix FA(jFA,N,N),FB(jFC,N,N),PA(jPA,N,N),PB(jPC,N,N);
        diisControl.NextCycle(FA,FB,PA,PB);
        QFree(jFC);
        QFree(jPC);
        EMax = diisControl.CurrentError();
      }
      else{
        //DIIS.NextCycle(FA,FB,PA,PB);
        if (!MP2Restart) diisControl.NextCycle(FA,FB,PA,PB);
        EMax = diisControl.CurrentError();
      }
      if (IPrint >= 2) {
        MatPrint(jFA,N,N,"Extrapolated Alpha Fock Matrix",4);
        if (NDen == 2) MatPrint(jFB,N,N,"Extrapolated Beta Fock Matrix",4);
      }
      // Save a copy of the latest Fock matrices; they may be needed later
      // for various purposes (getting canonical MOs, Fock fitting...)
/*
      // Perform EDA for FRZ and POL terms
      if (rem_read(REM_DO_E_DECOMP)>0 && LPSCFMI>0) {

        if (IteSCF==1) {
          //cout << "SAVE FRZ components" << endl;
          Get_ALMO_EDA(jF_EDA_copy,NDen-1,0); // Arguments: Fock, BetaSeparate?, POL?
          //if (NDen==2) Get_ALMO_EDA(jF_EDA_copy+N2,1,0);
        }

        if (EMax < Cnverg) {
          //cout << "SAVE POL components" << endl;
          Get_ALMO_EDA(jF_EDA_copy,NDen-1,1);
          //if (NDen==2) Get_ALMO_EDA(jF_EDA_copy+N2,1,1);
        }
	QFree(jF_EDA_copy);

      }
*/
      if ((!dc_dft && !dscf_eda) || (dc_dft && !have_dftE) || (dscf_eda && !have_dftE))
      {
         FileMan_Open_Write(FILE_TEMP_FOCK);
         FileMan(FM_WRITE,FILE_TEMP_FOCK,FM_DP,N*N,0,FM_BEG,jFA);
         FileMan(FM_WRITE,FILE_TEMP_FOCK,FM_DP,N*N,0,FM_CUR,jFB);
         FileMan_Close(FILE_TEMP_FOCK);
      }
      QTimerOff(t3,tdf2m);
      if(rem_read(REM_PRINT_SCF_TIME)>0)
      printf(" DIIS time:  CPU %.2f s  wall %.2f s\n",t3[0],t3[2]);
      /* Allocate for the MOs and eigenvalues */
      //!!!!!!!!!! reuse for P?
      if (jCA == NULL) {
	 jCA = QAllocDouble(NBasis*NOrb*NMO);
	 jCB = jCA + NBasis*NOrb*(NMO-1);
      }
      if (jEA == NULL) {
	 jEA = QAllocDouble(NOrb*NMO);
	 jEB = jEA + NOrb*(NMO-1);
      }

      tdf2m = QTimerOn();

      //RST:
      qtime_t timer0;
      timer0 = QTimerOn();

      if (!MP2Restart){

         if ( LPSCFMI > 0 && !(EMax < Cnverg && (RStep||ARStep)) ) { // ALMO-restricted Roothaan step
           //fock matrix is messed up by this call
           if (NMO == 1)
               Fock2MONON(jCA,jEA,jFA,0);
           else if (NMO == 2)
           {
               if(NAlpha>0) Fock2MONON(jCA,jEA,jFA,0); //PRH - part of an attempt to deal with zero dim subspaces, but
               if(NBeta>0) Fock2MONON(jCB,jEB,jFB,1);  // reliance on BLMatrix throughout the fragment code means
                                                       // that rewrites of BLMatrix for zero dim blocks is necessary
           }
         }
         else {  // No ALMO restriction

           INTEGER NVO = rem_read(REM_NVO_METHOD);

           if ( LPSCFMI > 0 ) {
             if ( ARStep ) {
               printf("Last iteration: ARS correction\n");
             }
             else
               printf("Last iteration: RS correction\n");
           }

           //LOGICAL BlockedMOs = (LPSCFMI>0 || (GuessImpr>=10 && IteSCF==1));
           LOGICAL NVOalgtm = (NVO>0 &&  EMax<NVOStart) || ARStep || RStep || ARS_no_scfmi;

           if (NVOalgtm) {
             if (ARStep || RStep || ARS_no_scfmi) {
               NVOstepNON(jCA,jFA,FALSE,EMax);
             }
             else {
               double *jXA=NULL;
               FileMan(FM_READ,FILE_MO_COEFS,FM_DP,N*NOrb,0,FM_BEG,jCA);
               NVOstep(jCA,jFA,jXA,FALSE,EMax);
             }
             VRload(jEA,NOrb,0.0);
           }
           else {
             if (rem_read(REM_DIIS_ERROR_VEC_DM2MO) > 0) {
               double label=0.0;
               FileMan(FM_WRITE,FILE_MO_COEFS_OAO,FM_DP,1,0,FM_BEG,&label);
               rem_write(1,REM_DIIS_ERROR_VEC_ACTIVE);
             }
	     if (rem_read(REM_CDFTCI_FRAGMENT) > 0) {
	       Fock2MOBlockCDFTCI(jCA,jEA,jFA,NAlpha,1);
	     } else {
               Fock2MO(jCA,jEA,jFA); // Standard DIIS Fock2MO
	     }
             if (rem_read(REM_ROKS)>0 && !Converged)
               VRcopy(jCAXC,jCA,N*NOrb);
           }

           // the same for beta
           if (NMO == 2) {
             if (NVOalgtm) {
               if (ARStep || RStep || ARS_no_scfmi) {
                 // RST!
                 //QCrash("NYI for unrestricted methods");
                 NVOstepNON(jCB,jFB,TRUE,EMax);
               }
               else {
                 double *jXB=NULL;
                 FileMan(FM_READ,FILE_MO_COEFS,FM_DP,N*NOrb,N*NOrb,FM_BEG,jCB);
                 NVOstep(jCB,jFB,jXB,TRUE,EMax);
               }
               VRload(jEB,NOrb,0.0);
             }
             else {
               if (rem_read(REM_DIIS_ERROR_VEC_DM2MO) > 0) {
                 double label=1.0;
                 FileMan(FM_WRITE,FILE_MO_COEFS_OAO,FM_DP,1,0,FM_BEG,&label);
                 rem_write(1,REM_DIIS_ERROR_VEC_ACTIVE);
               }
               if (rem_read(REM_CDFTCI_FRAGMENT)>0) {
                  Fock2MOBlockCDFTCI(jCB,jEB,jFB,NBeta,2);
               } else {
                  Fock2MO(jCB,jEB,jFB);
               }
             }
           } // end beta diag

         } //end normal diag

      } //end !MP2Restart

#ifdef RUSTY
      double timer1[3];
      QTimerOff(timer1,timer0);
      printf("TIMEINFO: Fock to MO CPU %.2f sec\n",timer1[0]);
      //endRST
#endif
     threading_policy::pop();
      QTimerOff(t3,tdf2m);

      if(rem_read(REM_PRINT_SCF_TIME)>0)
	printf(" Fock2MO time:  CPU %.2f s  wall %.2f s\n",t3[0],t3[2]);

      // Free the square Fock matrices
      QFree(jFA);
    } // End of Fock2MO block


    //ATG Maximum Overlap Method for determining the new orbitals
    INTEGER DoMOM = rem_read(REM_MOM_START);
//AJWT metadynamics
    mf.ModifyMOM(DoMOM,IteSCF);
// /AJWT
    if (DoMOM >= 1 && IteSCF >= DoMOM) {
      // Starting at cycle 1 with SAD is a no go.
      if (IteSCF == 1 && rem_read(REM_IGUESS) == SAD) {
	QWarn("Can not start MOM on the first SCF cycle with SAD");
      }else {
	MOMOrbitals(jCA,jEA,NAlpha,NBasis,NOrb,1);
	if (NMO == 2) {
	  MOMOrbitals(jCB,jEB,NBeta,NBasis,NOrb,2);
	}
      }
    }

    //AML
    if(NoSCF && (rem_read(REM_SET_LOCAL) <= 0)){ //KDC
      printf("Avoiding writing the new MOs to disk !!! \n");
      //AML
    }
    else if (usingNEGF) {

                    FileMan(FM_READ,FILE_DENSITY_MATRIX,FM_DP,N2,0,FM_BEG,jPA);
      if(NDen == 2) FileMan(FM_READ,FILE_DENSITY_MATRIX,FM_DP,N2,0,FM_CUR,jPB);
      if(IteSCF==1) printf("Skiping MO2Den\n");

    }


    else {
      // Construct the new densities
      //RST: use MO2DenNON for non-orthogonal MOs

      qtime_t tmm;
      tmm = QTimerOn();

      if ( LPSCFMI > 0 && !(EMax < Cnverg && (RStep||ARStep)) ) {

        INTEGER* iOcc_A = QAllocINTEGER(NAlpha);
        INTEGER* iOcc_B = QAllocINTEGER(NBeta);
        GetVOString(iOcc_A,0); // re-arrange vo orbitals, ALPHA!
        GetVOString(iOcc_B,1);  // TB_EDIT

        double* jCAback = QAllocDouble(NBasis*NOrb*NMO);
        double* jCBback = jCAback + NBasis*NOrb*(NMO-1);
        double* jEAback = QAllocDouble(NOrb*NMO);
        double* jEBback = jEAback + NOrb*(NMO-1);

        VRcopy(jCAback,jCA,N*NOrb);
        VRcopy(jEAback,jEA,  NOrb);
        VRcopy(jCBback,jCB,N*NOrb); //TB_EDIT
        VRcopy(jEBback,jEB,  NOrb);

        selocc(jCA,jEA,jCAback,jEAback,&N,iOcc_A,&NAlpha);
        selocc(jCB,jEB,jCBback,jEBback,&N,iOcc_B,&NBeta);  // TB_EDIT

        QFree(iOcc_A);
        QFree(iOcc_B);  // TB_EDIT
        QFree(jCAback);
        QFree(jEAback);

        MO2DenNON(jPA,jCA,N,NAlpha,0);
        MO2DenNON(jPB,jCB,N,NBeta,1);

      }
      else {
#ifdef JKN
// ---------------------------------------------------------------------
  tdm2d = QTimerOn();
// ---------------------------------------------------------------------
#endif
        if (fractional_occupations > 0) {
          // fractional SCF occupations (DSL)
          const int NAct = rem_read(REM_FON_NORB); // number of active orbitals

          double Temp = T;
          //cout << "Converged = " << Converged << endl;
          //cout << "Converged = " << rem_read(REM_SCF_CONVERGED) << endl;
          /*
          if (EMax < Cnverg*10.0) {
            Temp = 5.0;
            cout << "*** ZERO-KELVIN EXTRAPOLATION ***" << endl;
            //Converged = False;
          }
          */

          MO2DenFrac(jPA,jCA,jEA,N,0,NAlpha,false,Temp,NAlpha,NAct,EMax);
          if (NDen == 2) {
            MO2DenFrac(jPB,jCB,jEB,N,0,NBeta,false,Temp,NBeta,NAct,EMax);
          }
        }
#ifdef REM_TAO_DFT
         else if (rem_read(REM_TAO_DFT)>0){
#ifndef FILE_SPIN_NOONS
           double *noons=QAllocDouble(2*N);
#endif
           ETot -= EtsA + EtsB;
           TMO2Den(jPA,noons,jCA,jEA,N,1,NAlpha,NOrb,Theta,Ets);
           EtsA = Ets[0];
           printf(" EtsA = %16.10f\n", EtsA);

           if (NDen == 2) TMO2Den(jPB,noons+N,jCB,jEB,N,1,NBeta,NOrb,Theta,Ets);
           EtsB = Ets[0];
           printf(" EtsB = %16.10f\n", EtsB);
           if (IPrint > 1) {
               printf(" Using new entropy values:\n");
               printf(" Minus  Theta * Entropy = %16.12f\n",EtsA + EtsB);
           } else if (IPrint == 1) {
               printf(" Using new entropy values:\n");
               printf(" Minus  Theta * Entropy = %16.10f\n",EtsA + EtsB);
           }
           ETot += EtsA + EtsB;
// print TAO_GAP (SZL/2024)
           if (NDen == 2) {
             // Unrestricted case
             TAO_PROP(2,jEA,NAlpha,jEB,NBeta,NOrb,Theta);
           }else{
             // Restricted case
             TAO_PROP(1,jEA,NAlpha,jEA,NAlpha,NOrb,Theta);
           }
//         for the pTAO method
           if ((rem_read(REM_SET_ROOTS) > 0) && (EMax < Cnverg)){
             printf(" Reset TOONs to construct the pTAO reference state.\n");
             Itheta = 0.0;
             TMO2Den(jPA,noons,jCA,jEA,N,1,NAlpha,NOrb,&Itheta,Ets_fake);
             if (NDen == 2) TMO2Den(jPB,noons+N,jCB,jEB,N,1,NBeta,NOrb,&Itheta,Ets_fake);
           }
#ifndef FILE_SPIN_NOONS
           QFree(noons);
#endif
        }
#endif
        else {
          MO2Den(jPA,jCA,N,1,NAlpha);


          // JMH(11/2014) - this is NOT the pFON convergence algorithm.  Rather, it is
          // doing an SCF calculation with an actual fractional number of electrons.
          if (hasFracElec) AddFractionalElectron(jPA,jCA);


          if (NDen == 2) MO2Den(jPB,jCB,N,1,NBeta);
          if (rem_read(REM_SMX_SOLVATION) == -1) {
             INTEGER NAlpha2 = rem_read(REM_NALPHA2);
             INTEGER NBeta2 = rem_read(REM_NBETA2);
             if (NAlpha2 > NAlpha) MO2Den(jPA,jCA,N,1,NAlpha2);
             if (NDen == 2 && NBeta2 > NBeta) MO2Den(jPB,jCB,N,1,NBeta2);
          }
        }

#ifdef JKN
// ---------------------------------------------------------------------
  QTimerOff(t3,tdm2d);
  printf(" MO2Den  time:  CPU %.2f s  wall %.2f s\n",t3[0],t3[2]);
// ---------------------------------------------------------------------
#endif

      }

      if (fractional_occupations > 0) {
        // Scale temperature for fractional occupation algorithm (DSL)
        ScaleTemperature(T, EMax, IteSCF, T_start, T_end);
      }

#ifdef RUSTY
      double tmm1[3];
      QTimerOff(tmm1,tmm);
      printf("TIMEINFO: MO to DEN CPU %f sec \n",tmm1[0]);
#endif

      // Save energies for EDA and charges for CDA
      // EDA job or BSSE correction job or FRAGMO guess used
      // YMao removed the FRAGMO guess case and hopefully
      // that won't break anything (11/19)
      if (rem_read(REM_DO_E_DECOMP)>0 || rem_read(REM_ARS_BSSE_SUBSYSTEM)>0) {
        for (INTEGER IsBeta=0; IsBeta<NMO; IsBeta++) {
           if((IsBeta==0 && NAlpha>0) || (IsBeta==1 && NBeta>0))
           {  // TB_EDIT
             double *t=QAllocDouble(EFLength);
             t[0] = ETot;
             t[1] = E1;
             t[2] = EJ;
             t[3] = EKA;
             t[4] = EKB;
             t[5] = EX;
             t[6] = EC;
             double ET = E1 - EV;
             t[7] = ET;
             t[8] = ENuclear;
             t[9] = EV;

             double* jALMO=QAllocDouble(N*NOrb); // o1,o2,..,v1,v2,.. order
             FileMan(FM_READ,FILE_FRGM_MO_COEFS,FM_DP,N*NOrb,N*NOrb*IsBeta,FM_BEG,jALMO);

             double* pointerC=NULL;
             if (IsBeta) pointerC=jCB;
             else pointerC=jCA;

             LOGICAL rs_or_ars_bsse = (rem_read(REM_ARS_BSSE_SUBSYSTEM)==1 ||
               rem_read(REM_ARS_BSSE_SUBSYSTEM)==2);
             LOGICAL scf_bsse = (rem_read(REM_ARS_BSSE_SUBSYSTEM)==7);
             LOGICAL fragmo = (rem_read(REM_IGUESS)==FRAGMO);

             if ( IteSCF==1 && (LPSCFMI>0 || rs_or_ars_bsse) ) {
               //cout << "SAVE 1" << endl;
               Collect_EDA_Data(0,EFLength,t,pointerC,jALMO,IsBeta);
             }
             if (IteSCF==1 && fragmo && rem_read(REM_FRGM_LPCORR_SWITCH)==0 ) {
               Collect_EDA_Data(-1,EFLength,t,pointerC,jALMO,IsBeta);
             }

             if (EMax < Cnverg) {
               if (LPSCFMI>0) {
                 //cout << "SAVE 2" << endl;
                 Collect_EDA_Data(1,EFLength,t,pointerC,jALMO,IsBeta);
               }
               else {
                 if (rem_read(REM_FRGM_LPCORR_SWITCH)==1) {
                   //cout << "SAVE 4" << endl;
                   Collect_EDA_Data(3,EFLength,t,pointerC,jALMO,IsBeta);
                 }
                 else {
                //cout << "SAVE 3" << endl;
                   Collect_EDA_Data(2,EFLength,t,pointerC,jALMO,IsBeta);
                 }
               }

               if (scf_bsse) Collect_EDA_Data(0,EFLength,t,pointerC,jALMO,IsBeta);
               if (fragmo) Collect_EDA_Data(-1,EFLength,t,pointerC,jALMO,IsBeta);

             }

             QFree(jALMO);
             QFree(t);
           } //TB_EDIT END of if to check if occ

        }
      }

//ALMO population analysis
//      if ((RStep||ARStep||LPCorrExact)) {
//        double* jALMO=QAllocDouble(N*NOrb); // o1,o2,..,v1,v2,.. order
//        FileMan(FM_READ,FILE_FRGM_MO_COEFS,FM_DP,N*NOrb,0,FM_BEG,jALMO);
//        ALMO_Population(jCA,jALMO,0);
//        if (NMO==2) {
//          FileMan(FM_READ,FILE_FRGM_MO_COEFS,FM_DP,N*NOrb,N*NOrb,FM_BEG,jALMO);
//          ALMO_Population(jCB,jALMO,1);
//        }
//        QFree(jALMO);
//      }
//end ALMO population analysis

      // dual basis
      // RST modified if statement
      if ((rem_read(REM_SMALL_BASIS_LARGE_BASIS) == 1 && rem_read(REM_DUAL_BASIS_ENERGY) == 1) ||
          ((RStep||ARStep) && EMax < Cnverg) || (GuessImpr>0) ) {
        double Ecorrection = 0;
	for(int i=0; i<NBasis*NBasis; i++)
	  Ecorrection += (jPA[i]-jPold[i])*jFold[i];
	if (NDen == 2)
	  for(int i=0; i<NBasis*NBasis; i++)
	    Ecorrection += (jPB[i]-jPold[i+N2])*jFold[i+N2];
	else
	  Ecorrection *= 2.0;
    //Scale dual-basis correction for DFT jobs with a small 6-4G basis
      BasisType SmallBasis(rem_read(REM_BASIS2));
      if ((rem_read(REM_SMALL_BASIS_LARGE_BASIS) == 1 && rem_read(REM_DUAL_BASIS_ENERGY) == 1) && SmallBasis.Name() == "r64G" &&  (rem_read(REM_LEVEXC)>0) )
      {
		  printf("Scaling dual-basis correction for 6-4G DFT calculation...\n");
		  printf("  Unscaled Dual-Basis Correction: %14.10f\n", Ecorrection);
		  Ecorrection *= DBScaleFactor();
		  printf("  Scaled   Dual-Basis Correction: %14.10f\n\n", Ecorrection);
      }

        //RST output
	if (ARStep || RStep) {
          printf("SCF MI energy: %.10f\n", ETot);
          //printf("SCF MI(tARS-ERS) energy correction: %.10f\n",Ecorrection);
          //printf("SCF MI(tARS-ERS) energy: %.10f\n",ETot+Ecorrection);

          if (ARStep) {
            INTEGER Fr=rem_read(REM_FRAGMENTS);
	    double* E2xy=QAllocDouble(Fr*Fr);

            FileMan(FM_READ,FILE_ED_CT_DECOMP,FM_DP,Fr*Fr,0,FM_BEG,E2xy);
            double EtotARS[1];
            VRtrace(EtotARS,E2xy,Fr*Fr);
            if (NDen==2) {
              double* E2xyBeta = QAllocDouble(Fr*Fr);
              FileMan(FM_READ,FILE_ED_CT_DECOMP,FM_DP,Fr*Fr,1*Fr*Fr,FM_BEG,E2xyBeta);
              double EtotARSBeta[1];
              VRtrace(EtotARSBeta,E2xyBeta,Fr*Fr);
              EtotARS[0]+=EtotARSBeta[0];
              //printf("SCF MI(ARS) energy correction: %.10f\n",EtotARS[0]);
              //MatPrint(E2xy,Fr,Fr,"Alpha Charge Transfer Energy Components: Row->Col");
              //MatPrint(E2xyBeta,Fr,Fr,"Beta Charge Transfer Energy Components: Row->Col");
            }
            else {
              VRscale(E2xy,Fr*Fr,2.0);
              EtotARS[0]*=2.0;
              //printf("SCF MI(ARS) energy correction: %.10f\n",EtotARS[0]);
              //MatPrint(E2xy,Fr,Fr,"Charge Transfer Energy Components: Row->Col");
            }
            QFree(E2xy);
            Ecorrection=EtotARS[0];
          }

          printf("SCF MI(%s) energy: %.10f\n",(RStep?"RS":"ARS"),ETot+Ecorrection);

          if (rem_read(REM_DO_E_DECOMP)>0) {
            double *t=QAllocDoubleWithInit(EFLength);
            t[0] = ETot+Ecorrection;
            FileMan(FM_WRITE,FILE_ED_SUPERMOL,FM_DP,EFLength,2*EFLength,FM_BEG,t);
            QFree(t);
          }

	}
/*      else if (RStep) {
          printf("SCF MI energy: %.10f\n", ETot);
          //printf("SCF MI(RS) energy correction: %.10f\n",Ecorrection);
          printf("SCF MI(RS) energy: %.10f\n",ETot+Ecorrection);
          // Save energies for EDA
          if (rem_read(REM_DO_E_DECOMP)>0) {
            double *t=QAllocDoubleWithInit(EFLength);
            t[0] = ETot+Ecorrection;
            FileMan(FM_WRITE,FILE_ED_SUPERMOL,FM_DP,EFLength,2*EFLength,FM_BEG,t);
          }
        }
*/
        else if (GuessImpr>0 && IteSCF==1) {
          printf("Energy of the initial guess: %.10f\n", ETot);
          double ESRSCorrected = ETot + Ecorrection;
          if (ARS_no_scfmi) {
            //printf("tARS-ERS correction to the guess: %.10f\n",Ecorrection);
            //printf("tARS-ERS energy: %.10f\n",ESRSCorrected);

            INTEGER Fr=rem_read(REM_FRAGMENTS);
            if (rem_read(REM_ARS_BSSE_SUBSYSTEM)>0)
              FileMan(FM_READ,FILE_FRGM_PARTITION,FM_INT,1,0,FM_BEG,&Fr);

            double* E2xy=QAllocDouble(Fr*Fr);

            if (rem_read(REM_SUBSYSTEM)==1)
              FileMan(FM_READ,FILE_ED_BSSE_DECOMP,FM_DP,Fr*Fr,0,FM_BEG,E2xy);
            else
              FileMan(FM_READ,FILE_ED_CT_DECOMP,FM_DP,Fr*Fr,0,FM_BEG,E2xy);

            double EtotARS[1];
            VRtrace(EtotARS,E2xy,Fr*Fr);
            if (NDen==2) {
              double* E2xyBeta = QAllocDouble(Fr*Fr);
              if (rem_read(REM_SUBSYSTEM)==1)
                FileMan(FM_READ,FILE_ED_BSSE_DECOMP,FM_DP,Fr*Fr,1*Fr*Fr,FM_BEG,E2xyBeta);
              else
                FileMan(FM_READ,FILE_ED_CT_DECOMP,FM_DP,Fr*Fr,1*Fr*Fr,FM_BEG,E2xyBeta);
              double EtotARSBeta[1];
              VRtrace(EtotARSBeta,E2xyBeta,Fr*Fr);
              EtotARS[0]+=EtotARSBeta[0];
            }
            else {
              VRscale(E2xy,Fr*Fr,2.0);
              EtotARS[0]*=2.0;
            }
            printf("%s energy correction to the guess: %.10f\n",(GuessImpr==15?"ARS":"RS"),EtotARS[0]);
            printf("%s energy: %.10f\n",(GuessImpr==15?"ARS":"RS"),ETot+EtotARS[0]);
            QFree(E2xy);
            Ecorrection=EtotARS[0];
          } // end ARS_no_mi
          else {
            printf("Single RS correction to the guess: %.10f\n",Ecorrection);
            printf("Corrected energy: %.10f\n",ESRSCorrected);
          }
        }
        else if (GuessImpr>0 && IteSCF==2) {
          double EDRSCorrected = ETot + Ecorrection;
          printf("Energy before correction: %.10f\n", ETot);
          printf("Double RS energy correction: %.10f\n",Ecorrection);
          printf("Corrected energy: %.10f\n",EDRSCorrected);
        }
        else {
          printf(" ETot: %20.12f\n", ETot);
          printf(" dual-basis energy correction: %20.12f\n",Ecorrection);
        }

        ETot += Ecorrection;

        FileMan(FM_WRITE,FILE_ENERGY,FM_DP,1,FILE_POS_CRNT_TOTAL_ENERGY,FM_BEG,&ETot);
        FileMan(FM_WRITE,FILE_ENERGY,FM_DP,1,FILE_POS_SCF_ENERGY,       FM_BEG,&ETot);

        QFree(jPold);
        QFree(jFold);

      }
      //endRST

// !RST ----
//        if (!usingGDM && !usingDM) MatPrint(jEA,1,NOrb,"Alpha MO Eigenvalues");
//        if (NMO == 2) {
//          if (!usingGDM && !usingDM && !usingGDIIS ) MatPrint(jEB,1,NOrb,"Beta MO Eigenvalues");
//        }
/// RST! ----- end

      if (IPrint >= 2) {
	L = min(N,NAlpha+5);
	if (!usingGDM && !usingDM) MatPrint(jEA,1,L,"Alpha MO Eigenvalues");
	if (IPrint >= 2) {
	  MatPrint(jCA,N,L,"Alpha MO Coefficients");
	  MatPrint(jPA,N,N,"Alpha Density Matrix");
	}
	if (NMO == 2) {
	  L = min(N,NBeta+5);
	  if (!usingGDM && !usingDM && !usingGDIIS ) MatPrint(jEB,1,L,"Beta MO Eigenvalues");
	  if (IPrint >= 2) MatPrint(jCB,N,L,"Beta MO Coefficients");
	}
	if (NDen == 2 && IPrint >= 2)
	  MatPrint(jPB,N,N,"Beta Density Matrix");
      }
      /* Store the current MOs, eigenvalues and densities.  In case of
         MP2 restart they are already correct on disk and shouldn't be
         altered. */
      if (!MP2Restart){
         // RST do not save LPSCFMI corrected orbitals
         if (!(EMax < Cnverg && LPSCFMI > 0)) {
           if (npes() > 1 && DynamicDispatcher::canUse)
           {
              // need this broadcasting to fix GDM_phenyl and Hartree-Fock Freq jobs
              Broadcast(jCA, N*NOrb, 0);
              Broadcast(jCB, N*NOrb, 0);
           }

           FileMan(FM_WRITE,FILE_MO_COEFS,FM_DP,N*NOrb,0,FM_BEG,jCA);
           FileMan(FM_WRITE,FILE_MO_COEFS,FM_DP,N*NOrb,0,FM_CUR,jCB);
		   if (bSetMgr.crntCode() == bCodeprim ) {
			  FileMan(FM_WRITE,FILE_SMALL_BASIS_MO_COEFS,FM_DP,N*NOrb,0,FM_BEG,jCA);
			  FileMan(FM_WRITE,FILE_SMALL_BASIS_MO_COEFS,FM_DP,N*NOrb,0,FM_CUR,jCB);
		   }
           if (!usingGDM && !usingDM && !usingGDIIS && !usingNEGF) {
              FileMan(FM_WRITE,FILE_MO_COEFS,FM_DP,NOrb,0,FM_CUR,jEA);
              FileMan(FM_WRITE,FILE_MO_COEFS,FM_DP,NOrb,0,FM_CUR,jEB);
           }
           if (LPSCFMI>0 && EMax>Cnverg) {
             FileMan(FM_WRITE,FILE_FRGM_MO_COEFS,FM_DP,N*NOrb,0,FM_BEG,jCA);
             FileMan(FM_WRITE,FILE_FRGM_MO_COEFS,FM_DP,N*NOrb,0,FM_CUR,jCB);
             if (!usingGDM && !usingDM && !usingGDIIS && !usingNEGF) {
               FileMan(FM_WRITE,FILE_FRGM_MO_COEFS,FM_DP,NOrb,0,FM_CUR,jEA);
               FileMan(FM_WRITE,FILE_FRGM_MO_COEFS,FM_DP,NOrb,0,FM_CUR,jEB);
             }
           }

         //}
         }
      }

      // Decomposition of DeltaQ(SCF)
      LOGICAL Get_EDA_for_SCF = (  rem_read(REM_EDA_DECOMP_SCF) &&
        ( LPCorrExact || rem_read(REM_ARS_BSSE_SUBSYSTEM)==7 )   );
      if ( Get_EDA_for_SCF && EMax<Cnverg ) {
        double* fake_Fock=QAllocDouble(N2);
        double* fake_MOs=QAllocDouble(N*NOrb);
        FileMan(FM_READ,FILE_FOCK_MATRIX,FM_DP,N2,0,FM_BEG,fake_Fock);
        NVOstepNON(fake_MOs,fake_Fock,FALSE,0.000001);
        FileMan(FM_READ,FILE_FOCK_MATRIX,FM_DP,N2,N2,FM_BEG,fake_Fock); //PRH_EDIT open shell
        NVOstepNON(fake_MOs,fake_Fock,TRUE,0.000001);
        QFree(fake_MOs);
        QFree(fake_Fock);
      }
      // Decomposition of DeltaQ(SCF_MI)
      LOGICAL Get_EDA_for_SCF_MI = (  rem_read(REM_EDA_DECOMP_SCF_MI) && LPSCFMI
        && rem_read(REM_EDA_FRZ_BASIS)!=0 && LPCorr==0  );
      if ( Get_EDA_for_SCF_MI && EMax<Cnverg ) {
        double* fake_Fock=QAllocDouble(N2);
        double* fake_MOs=QAllocDouble(N*NOrb);
        FileMan(FM_READ,FILE_FOCK_MATRIX,FM_DP,N2,0,FM_BEG,fake_Fock);
        NVOstepNON(fake_MOs,fake_Fock,FALSE,0.000001);
        FileMan(FM_READ,FILE_FOCK_MATRIX,FM_DP,N2,N2,FM_BEG,fake_Fock); //PRH_EDIT open shell
        NVOstepNON(fake_MOs,fake_Fock,TRUE,0.000001);
        QFree(fake_MOs);
        QFree(fake_Fock);
      }

    }

#ifdef JKN
      sparsity2(jPA,N2,-1,1,fake_timer,fake_timer,"PA");
      if (NDen == 2) sparsity2(jPB,N2,-1,1,fake_timer,fake_timer,"PB");
#endif

#ifdef RUSTY
    //RST: time scf
    QTimerOff(rusty41,rusty40);
    printf("TIMEINFO->: F2Den %.2f sec.\n",rusty41[0]);
#endif

    if (rem_read(REM_DOMOS_DFT) > 0 || XCFunc.HasTau() || rem_read(REM_ROKS)>0) {
      if (rem_read(REM_ROKS)>0)
        VRcopy(jCAXC,jCA,NBas6D*NOrb*NMO);
      else
      {
        VRcopy(jCAXC,jCA,N*NOrb*NMO);
        if(LPSCFMI > 0) {
           OrthogonalizeMOs(jCAXC, N, NOA);  //YMao: orthogonalize occ ALMOs and feed them into DFTMan (feeding non-ortho MOs is invalid)
           if (NMO > 1) {OrthogonalizeMOs(jCAXC+N*NOrb, N, NOB);}
        }
      }
    }

    if (usingNEGF){
      if(IteSCF==1) printf("Fock density Matrix written outside\n");
      FileMan(FM_WRITE,FILE_DENSITY_MATRIX,FM_DP,N2,0,FM_BEG,jPA);
      FileMan(FM_WRITE,FILE_DENSITY_MATRIX,FM_DP,N2,0,FM_CUR,jPB);
    }


    // db-mp2, need one more fock build for mp1
    if(rem_read(REM_DBMP2_SINGLES) == 1 && rem_read(REM_SMALL_BASIS_LARGE_BASIS) == 1 ) {
        dbmp2_singles_fock_build(jPA, jPB, NDen, NBasis, NBas6D, NB2, NB2car,
        IPrint, NDeriv, VThresh, UseIntScreen, Use_dP, IteSCF);
    }

    //RST - if statement
    // Save density unless LP SCF is converged
    //if (!(EMax < Cnverg && LPSCFMI > 0 )) {
      FileMan(FM_WRITE,FILE_DENSITY_MATRIX,FM_DP,N2,0,FM_BEG,jPA);
      FileMan(FM_WRITE,FILE_DENSITY_MATRIX,FM_DP,N2,0,FM_CUR,jPB);

      if(rem_opsing == 1)
      { // NAB for open shell singlet
          if(rem_read(REM_TRIPLET) == 1)
          {
             FileMan(FM_WRITE,FILE_DENS_T_MATRIX,FM_DP,N2,0,FM_BEG,jPA);
             FileMan(FM_WRITE,FILE_DENS_T_MATRIX,FM_DP,N2,0,FM_CUR,jPB);
          }else{
             FileMan(FM_WRITE,FILE_DENS_S_MATRIX,FM_DP,N2,0,FM_BEG,jPA);
             FileMan(FM_WRITE,FILE_DENS_S_MATRIX,FM_DP,N2,0,FM_CUR,jPB);
          }
      }

      ScaV2M(jPA,jPAv,True,False);
      if (NDen == 2) ScaV2M(jPB,jPBv,True,False);

      FileMan_Open_Write(FILE_SPARSE_DENSITY_MATRIX);
      FileMan(FM_WRITE,FILE_SPARSE_DENSITY_MATRIX,FM_DP,NB2,0,FM_BEG,jPAv);
      if (NDen == 2)
        FileMan(FM_WRITE,FILE_SPARSE_DENSITY_MATRIX,FM_DP,NB2,0,FM_CUR,jPBv);
      else
        FileMan(FM_WRITE,FILE_SPARSE_DENSITY_MATRIX,FM_DP,NB2,0,FM_CUR,jPAv);
      FileMan_Close(FILE_SPARSE_DENSITY_MATRIX);
    //}

    /* For pure DFT we don't need square P's anymore.
       Create sparse versions for next SCF cycle. */
    /* except for dual-basis, when we still need jPA for a bit (freed later) */
    // BJAc Also need jPA still for embedding (freed later)
   // And for SCF SaveMinima
    if ( XCFunc.IsPureDFT() && !(add_LRK || LRC ||mf.iSaveMinima) && !rem_read(REM_ROKS) &&
         rem_read(REM_SMALL_BASIS_LARGE_BASIS)!=1 && !rem_read(REM_EMBED_INTERNAL) &&
         ((!dc_dft && !dscf_eda) || (dc_dft && have_hfdens) || (dscf_eda && have_hfdens)) ) 
    {
      QFree(jPA);
    }
#if 0
    if ( rem_read(REM_INCDFT) > 0 && EMax < Cnverg*10000.0 && !IncDFTDIISReset )
      {
	printf("Reseting DIIS.\n");
	DIIS.Reset();
	IncDFTDIISReset = TRUE;
      }
#endif

    if(IteSCF == MaxSCF && rem_read(REM_HIRSHFELD_ACTIVE) && EMax > Cnverg) { //@@SY
      Converged = TRUE;
      rem_write(1,REM_SCF_CONVERGED);
    }

//NAB converge first cycle for MOM

     if(MOMFroz){
       printf("\n** Force Convergence and Restore Orbitals\n");
       Converged = TRUE;
       rem_write(1,REM_SCF_CONVERGED);
       FileMan(FM_READ,FILE_MO_COEFS,1,N*NOrb,0,1,jCA);
       FileMan(FM_READ,FILE_MO_COEFS,1,N*NOrb,0,2,jCB);
     }

//stop crash for basin hopping calculations
   if(rem_read(REM_SCF_NOCRASH) == 1 && IteSCF == MaxSCF){
      printf("\n** Carry on calculation\n");
      Converged = TRUE;
      rem_write(1,REM_SCF_CONVERGED);
   }

    /* Print the energy and check for convergence */

    //    if(SCFConv.doingSVP() && !SVP_Conv){printf("\nSVP_has not Converged!!!\n");}
    if (((EMax > Cnverg || IteSCF == 1 || !ConvOK && !rem_read(REM_IDEMPOTENT_GUESS))
        || (SCFConv.doingSVP() && !SVP_Conv)) && !NoSCF && ((!dc_dft && !dscf_eda) 
        || (dc_dft && !have_hfdens) || (dscf_eda && !have_hfdens))
        || !cdft_converged) 
    {

      if (rem_read(REM_SMALL_BASIS_LARGE_BASIS) == 1 && rem_read(REM_DUAL_BASIS_ENERGY) == 1)
	Comment = "    Including correction";
      else if (IteSCF == MaxSCF && rem_read(REM_HIRSHFELD_ACTIVE)) {
	Comment = "Hirshfeld: atomic densities failed to converge. Proceeding foolhardily."; //@@SY
        if (rem_read(REM_SMX_SOLVATION) == -1) QCrash("Failure to compute Hirshfeld charges");
      }
      else if (IteSCF == MaxSCF)
        Comment = "    Convergence failure";
      else if ((!usingGDM && !usingDM && !usingGDIIS && !UseRCA) && MetDIIS > 0) {
        if (EMax < ThrDIIS|| IteSCF == NBadDIIS) {
          if (canUseDM) {  /* Switch from DIIS to DM if requested */
            usingDM = True;
            Comment = " Done DIIS. Switching to DM";
          }
          else if (canUseGDM) {  /* Switch from DIIS to GDM if requested */
            usingGDM = True;
            Comment = " Done DIIS. Switching to GDM";
          }
          else if (canUseGDIIS) {  /* Switch from DIIS to GDIIS if requested */
            usingGDIIS = True; ItDM = -1;
            Comment = " Done DIIS. Switching to GDIIS";
          }
        }
      } else if((UseRCA) && MetDIIS>0){
	if (EMax < ThrRCA || IteSCF == NBadRCA) {
            UseRCA = False;  /* Switch from RCA to DIIS if requested */
            Comment = " Done RCA. Switching to DIIS";
          }
      }

      if (GuessImpr>0 && IteSCF==1) {
        if (ARS_no_scfmi) {
          if (GuessImpr==15) Comment = "    ARS corrected energy";
          else Comment = "    RS corrected energy";
        }
        else Comment = "    Single RS corrected energy";
      }

      if (GuessImpr==11 && IteSCF==2) {
        Comment = "    Double RS corrected energy";
      }
      else if (GuessImpr==20 && IteSCF==2) {
        Comment = "    SCF single RS energy";
      }


      if (IteSCF == 1) {
	if(SCFConv.doingSVP()){
	  printf(" -------------------------------------------------------\n");
	  if (usingGDM || usingDM )
	    printf("  Cycle       Energy        RMS Gradient   SVP Error\n");
	  else if(usingNEGF)
	    printf("  Cycle       Energy         NEGF Error\n");
	  else
	    printf("  Cycle       Energy         DIIS Error    SVP Error\n");
	  printf(" -------------------------------------------------------\n");
	}
	else {
	  printf(" ---------------------------------------\n");
	  if (usingGDM || usingDM || usingGDIIS)
	    printf("  Cycle       Energy        RMS Gradient\n");
	  else if(usingNEGF)
	    printf("  Cycle       Energy         NEGF Error\n");  //AY added
	  else
	    printf("  Cycle       Energy         DIIS Error\n");
	  printf(" ---------------------------------------\n");
	}
      }

#ifdef DEVELOPMENT
      if(SCFConv.doingSVP())
	printf("%5d%19.10lf%14.2E%14.2E     00000",IteSCF,ETot,EMax,SVP_Error);
      else{
	printf("%5d%19.10lf%14.2E  00000",IteSCF,ETot,EMax);
        if (IPrint > 0){
           double gap = jEA[NAlpha] - jEA[NAlpha-1];
           printf("  Gap = %.2f eV ",gap*ConvFac(HARTREES_TO_EV));
        }
      }
#else
      if(SCFConv.doingSVP())
	printf("%5d%19.10lf%14.2E%14.2E",IteSCF,ETot,EMax,SVP_Error);
      else{
	printf("%5d%19.10lf%14.2E",IteSCF,ETot,EMax);
        if (IPrint > 0){
           double gap = jEA[NAlpha] - jEA[NAlpha-1];
           printf("  Gap = %.2f eV ",gap*ConvFac(HARTREES_TO_EV));
        }
      }
#endif
      if (MP2Restart) Comment = "    SCF bypassed upon request";
      // EPIF - Need to use printf, not cout, to avoid an i/o bug
      if (!rem_read(REM_HIRSHFELD_ACTIVE)) printf("%s", Comment.c_str()); //@@SY
      printf("\n");
    }
    else if (SCFConv.UseFinalBuild()) 
    {
      // TRA - Temp Hack for a Final accurate build after SCF has converged..
      //       Needs some of the convergence stuff put in SCFConvControl??

      SCFConv.SetFinalBuild();

      if (rem_read(REM_SMALL_BASIS_LARGE_BASIS) == 1 && rem_read(REM_DUAL_BASIS_ENERGY) == 1)
	Comment = "    Including correction";
      else if (IteSCF == MaxSCF)
        Comment = "    Convergence failure";
      else if ((!usingGDM && !usingDM && !usingGDIIS) && MetDIIS > 0) {
        if (EMax < ThrDIIS|| IteSCF == NBadDIIS) {
          if (canUseDM) {  /* Switch from DIIS to DM if requested */
            usingDM = True;
            Comment = "Done DIIS. Switching to DM";
          }
          else if (canUseGDM) {  /* Switch from DIIS to GDM if requested */
            usingGDM = True;
            Comment = "Done DIIS. Switching to GDM";
          }
          if (canUseGDIIS) {  /* Switch from DIIS to GDIIS if requested */
            usingGDIIS = True;
            Comment = " Done DIIS. Switching to GDIIS";
          }
        }
      }

      if (GuessImpr>0 && IteSCF==1) {
        Comment = "    Initial guess energy";
      }
      else if (GuessImpr==11 && IteSCF==2) {
        Comment = "    Unperturbed energy";
      }
      else if (GuessImpr==20 && IteSCF==2) {
        Comment = "    Variational SRS energy";
      }

      if(SCFConv.doingSVP())
	printf("%5d%19.10lf%14.2E%14.2E     00000",IteSCF,ETot,EMax,SVP_Error);
      else
	printf("%5d%19.10lf%14.2E  00000",IteSCF,ETot,EMax);
      //      printf("%5d%19.10lf%14.2E %.2lf/%.2lf     %.2lf/%.2lf %s",IteSCF,ETot,EMax, t2[0],t2[1],t3[0],t3[1],Comment );
      // EPIF - Need to use printf, not cout, to avoid an i/o bug
      printf("%s\n", Comment.c_str());

      SCFConv.FinalBuildOff(); // Sets FinalBuild to Off so it will do one iter.
    }

    else{
      // If we are doing SVP, start this over
      if(SCFConv.UseSVP() && !SCFConv.doingSVP()){
	// Print out this iteration's energy
#ifdef DEVELOPMENT
	printf("%5d%19.10lf%14.2E  00000",IteSCF,ETot,EMax);
#else
	printf("%5d%19.10lf%14.2E",IteSCF,ETot,EMax);
#endif
        // EPIF - Need to use printf, not cout, to avoid an i/o bug
	printf("%s\n", Comment.c_str());

	printf("\nThe Gas Phase SCF has converged");
	printf("\n ---------------------------------------\n");
	printf("\n\n Now restarting with SVP Calculation");
	svpinfo.GasPhaseEnergy = ETot;
	EMax = 1.0E10;
	diisControl.Reset(0);
	IteSCF = 0;
	//	SCFConv.Reset();
	SCFConv.SwitchOnSVP();
      }
      else if ((!dc_dft && !dscf_eda) || (dc_dft && !Converged && !have_hfdens) || (dscf_eda && !Converged && !have_hfdens))
      {
       if(!mf.CheckNearConvergence(IteSCF,ETot,EMax)) //AJWT metadynamics
       {
         Converged = TRUE;
         if (Converged && dc_dft && !have_hfdens)
         {
            Converged = FALSE;
            have_hfdens = 1;
            printf("%5d%19.10lf%14.2E",IteSCF,ETot,EMax);
            printf(" Convergence criterion met for HF energy\n");
            printf("   Performing an additional SCF iteration to generate DFT Fock matrix\n");
            //rem_write(0,REM_INCFOCK); // JMH? 
            if (XCFunc.IsPureDFT()  && !(LRC || add_LRK)) DoJ = TRUE;
            VRcopy(jJv_temp,jJv,NB2car*NDen);
         }
         else{
            rem_write(1,REM_SCF_CONVERGED);
            if (rem_read(REM_ROKS)>0)
              FileMan(FM_WRITE,FILE_MO_COEFS,FM_DP,N*NOrb,0,FM_BEG,jCA);
            if(!ConvOK) {  Converged = FALSE;}
         }
// AJWT metadynamics
       }
// /AJWT
      }
    }

    //(check the end of adding bias voltage: finish or new iteration cycle)
    if(usingNEGF) if( Converged && tran_opt==4 ) {
	 printf("   %d NEGF Convergence criterion met at %f [eV] bias (%d-th point)\n",IteSCF,Vbias,iVbias);
	 int nVbias;
	 nVbias = rem_read(REM_TRANS_NVBIAS);
	 if( iVbias < nVbias ) {
	    Converged = FALSE;
	    IteSCF=0;  //reset iteration number
        libqchem::basic_display disp(std::cout);
        libqchem::output_handler task_output_handler(disp);
        qink_anlman().run(task_output_handler);
 	 } else if (iVbias==nVbias) {
	    printf("\n--- Converged at maximum bias voltage ---\n\n");
	 }
    }
    
    //AWL -- if converged here, do one more PCM iteration to get G_es from final SCF
    if(usePCM && Converged){

        // Modify a rem variable to let PCMman know we are on the final PCM call
        rem_write(1,REM_PCM_FINAL);
        // Subtract off the previous step's solvation energy to make room for the new one
        //ETot = ETot - jE_PCM[0]*0.5 - jE_PCM[5]*0.5;

        //Temporarily combine the split density matrices
        if (NDen == 1)
          VRscale(jPAv,NB2,2.0);
        else
          VRadd(jPAv,jPAv,jPBv,NB2);

        if(dofRF){
          if(rem_read(REM_PCM_NON_ELS) > 0 && rem_read(REM_QM_MM_INTERFACE) != JANUS)
            PCMman(PCMJOB_ELS_NONELS_ENERGY, jPAv, jE_PCM); //do non-electrostatic contributions
          else if(dofRF){
            PCMman(PCMJOB_EQ_SS_FRF, jPAv, jE_PCM); //do frozen reaction field SCF
          }else{
            PCMman(PCMJOB_ENERGY, jPAv, jE_PCM); //do common SCRF
          }
        }else
          scrf::instance().finalize(jPAv);

        // we will do a final print out of the energies later on...

        //Split density matrices back again
        if (NDen == 1)
          VRscale(jPAv,NB2,0.5);
        else
          VRsub(jPAv,jPAv,jPBv,NB2);
    }

    // LVS
    if (do_efp && Converged) {
        // do one more SCF iteration if polarization integrals weren't updated in the last one
        if (EFP2::instance().get_if_pol_field() && rem_read(REM_EFP_POL_FIELD_UPDATE) != 1) {
          Converged = FALSE;
          EFP2::instance().set_if_pol_field(TRUE);
        }
        //printf(" SCF pol_field %s \n", EFP2::instance().get_if_pol_field() ? "true":"false");
        //printf(" SCF converged %s \n", Converged ? "true":"false");
    }

      // BJA_Corr! Projection Correction
    if (rem_read(REM_EMBED_INTERNAL) && Converged )
    {
        cout << "Embed: Total SCF energy without projection correction: " << ETot << endl;
        double PProjtrace = 0;
        double *jPProjA = QAllocDoubleWithInit(NBasis*NBasis);
        AtimsB(jPProjA, jPAoriginal, jProjOpA, NBasis, NBasis, NBasis,NBasis, NBasis, NBasis, 1);
        if (IPrint >= 2) {
            MatPrint(jProjOpA, NBasis, NBasis, "jProjOpA");
        }
        VRscale(jPProjA, NBasis*NBasis, mufact);
        double trace = 0.0;
        for (int i=0; i < NBasis; i++ ) {
            trace += jPProjA[i + NBasis*i];
        }
        ETot += mufact * PProjtrace;
        cout << "Embed: Projection correction = " << mufact * PProjtrace << endl;
        cout << "Embed: Total SCF energy with projection correction: " << ETot << endl;
      // Free jPA here since embed_internal prevented it from being freed earlier
      QFree(jPA);
    }
//AJWT metadynamics
    mf.CheckConvergence(jCA,jCB,jPA,jPB,jPAv,jPBv,jEA,jEB,ETot,Converged,Cnverg,IteSCF,EMax);
    if(mf.GetNewOrbitals(jCA,jCB,jPA,jPB,jPAv,jPBv,jEA,jEB))
      mf.ResetMethods(IteSCF,NBadDIIS,canUseGDM,usingGDM,MetDIIS,MetSCF);
// /AJWT

    //Do not free jCA yet for the last cycle even unconverged, for
    //last printing.
    if (rem_read(REM_DUAL_BASIS_ENERGY)==1 && rem_read(REM_SMALL_BASIS_LARGE_BASIS)==1
        || LPNeedsOld || rem_read(REM_CDFTCI)!=0)
    {
       //We don't want to free these for DB calcs
#ifdef DEVELOPMENT
       cout << "Skipping free of jCA and jEA for dbscf\n";
#endif
       //QFree(jCA);
       //QFree(jEA);
    }
    else if ( !Converged && IteSCF != (MaxSCF - 1) && !MP2Restart)
    {
       QFree(jCA);
       QFree(jEA);
    }

    QTimerOff(t1,tdC);  /* Time the SCF */
    //    printf(" Cextrap. time:  CPU %.2f s  wall %.2f s\n",t1[0],t1[2]);
   if ((dc_dft && have_hfdens && have_dftE) || (dscf_eda && have_hfdens && have_dftE))
   {
        Converged = TRUE;
        rem_write(1,REM_SCF_CONVERGED);
        if (rem_read(REM_ROKS)>0)
           FileMan(FM_WRITE,FILE_MO_COEFS,FM_DP,N*NOrb,0,FM_BEG,jCA);
   }
  } /* IteSCF */

  // End of SCF Cycles
 

  // Calling MBD as a post-scf correction
  // Added by Thomas Markovich 02/2016
        // MBD = 1 means energy Only
        // MBD = 2 means energy + forces but no SC
        // MBD = 3 means energy + sc but no forces
        // MBD = 4 means energy + sc + forces
  // Modified by Szabolcs Goger 5/2022
  // 100 and 101 now call LibMBD (1-4 are not deleted for backwards compatibility)
  //
  // 100 is energy from LibMBD (no sc)
  // 101 is energy + force from LibMBD (no sc)
  // 102 is sc energy + forces from legacy implementation (same as 4)
  
        int MBD = rem_read(REM_MBDVDW);
        if(((MBD >= 1))){
            bool do_sc = ((MBD==3) || (MBD==4) || (MBD==102));
            bool do_force = ((MBD==2) || (MBD==4) || (MBD==101));
            bool do_library = ((MBD==100) || (MBD==101) || (MBD==102));
            compute_mbd(do_sc, do_force, do_library);
            ftn_mbdvdw_get_energy(&Edisp);
            cout << "MBDVDW|MBDVDW" << endl;
            printf("MBD vdW energy contribution: %11.10e au\n", Edisp);
            cout << "Will be added to SCF energy" << endl;
            cout << "MBDVDW|MBDVDW" << endl;
            ETot+=Edisp;
  }
  // finished call to apply MBD as a post-scf correction

  // dennisb:
  // Calling TS as post-scf correction
  // Added by Dennis Barton 08/2017
        // iTS = 1 means energy only
        // iTS = 2 means energy and forces
        // ...
        int iTS = rem_read(REM_TSVDW);
        if (iTS >= 1){
            bool do_force = (iTS==2);
            compute_ts(do_force);
            ftn_tsvdw_get_energy(&Edisp);
            cout << "TSVDW|TSVDW" << endl;
            printf("TS vdW energy contribution: %11.10e au\n", Edisp);
            cout << "Will be added to SCF energy" << endl;
            cout << "TSVDW|TSVDW" << endl;
            //Add energy to total energy
            ETot+=Edisp;
  }

// igor/ysj
  if(rem_read(REM_LEVEXC) == XCFUNC_XYG3 || rem_read(REM_LEVEXC) == XCFUNC_XYG3RI) { /* XYG3 functional */
    XCFunc = XYG3();
    IGrdDF_2 = pick_grid(rem_read(REM_IGRDTY),EMax,IteSCF,NBasis);
    rem_write(pick_XC_thresh(IGrdDF_2!=rem_read(REM_IGRDTY),EMax,Cnverg),
                     REM_DFT_THRESH);
    DFTman(&EX,&EC,jXCAv,jXCBv,jPAv,jCAXC,NULL,NULL,2,
           XCFunc,IGrdDF_2,IPrint-2,IteSCF, EMax);
    double xEKA = 0.8033/0.2*EKA;
    double xEKB = 0.8033/0.2*EKB;
    xETot = ENuclear + eNucSolvnt_old + eSolvnt_old + E1 + EJ + xEKA + xEKB
            + EX + EC + E_EFP + ESolv + E_born + Edisp + Eairbed;

    //FileMan(FM_WRITE,FILE_ENERGY,FM_DP,1,1,FM_BEG,&xETot);
    //Added by Kaushik for libdh
    EKA = xEKA;
    EKB = xEKB;
  }

  if(rem_read(REM_LEVEXC) == XCFUNC_QACFRI) { /* QACF functional */
    XCFunc = QACF();
    IGrdDF_2 = pick_grid(rem_read(REM_IGRDTY),EMax,IteSCF,NBasis);
    rem_write(pick_XC_thresh(IGrdDF_2!=rem_read(REM_IGRDTY),EMax,Cnverg),
                     REM_DFT_THRESH);
    DFTman(&EX,&EC,jXCAv,jXCBv,jPAv,jCAXC,NULL,NULL,2,
           XCFunc,IGrdDF_2,IPrint-2,IteSCF, EMax);
    double xEKA = 0.66666/0.25*EKA;
    double xEKB = 0.66666/0.25*EKB;
    xETot = ENuclear + eNucSolvnt_old + eSolvnt_old + E1 + EJ + xEKA + xEKB
            + EX + EC + E_EFP + ESolv + E_born + Edisp + Eairbed;
    //FileMan(FM_WRITE,FILE_ENERGY,FM_DP,1,1,FM_BEG,&xETot);
  }

  if(rem_read(REM_LEVEXC) == XCFUNC_XYGJOS || rem_read(REM_LEVEXC) == XCFUNC_LXYGJOS) { /* XYGJOS functional */
    XCFunc = XYGJOS();
    IGrdDF_2 = pick_grid(rem_read(REM_IGRDTY),EMax,IteSCF,NBasis);
    rem_write(pick_XC_thresh(IGrdDF_2!=rem_read(REM_IGRDTY),EMax,Cnverg),
                     REM_DFT_THRESH);
    DFTman(&EX,&EC,jXCAv,jXCBv,jPAv,jCAXC,NULL,NULL,2,
           XCFunc,IGrdDF_2,IPrint-2,IteSCF, EMax);
    double xEKA = 0.7731/0.2*EKA;
    double xEKB = 0.7731/0.2*EKB;
    xETot = ENuclear + eNucSolvnt_old + eSolvnt_old + E1 + EJ + xEKA + xEKB
            + EX + EC + E_EFP + ESolv + E_born + Edisp + Eairbed;
    //FileMan(FM_WRITE,FILE_ENERGY,FM_DP,1,1,FM_BEG,&xETot);
    //Added by Kaushik for libdh
    EKA = xEKA;
    EKB = xEKB;
  }

  if(rem_read(REM_LEVEXC) == XCFUNC_XYG_OS5) { /* XYG_OS5 functional */
    XCFunc = XYG_OS5();
    IGrdDF_2 = pick_grid(rem_read(REM_IGRDTY),EMax,IteSCF,NBasis);
    rem_write(pick_XC_thresh(IGrdDF_2!=rem_read(REM_IGRDTY),EMax,Cnverg),
                     REM_DFT_THRESH);
    DFTman(&EX,&EC,jXCAv,jXCBv,jPAv,jCAXC,NULL,NULL,2,
           XCFunc,IGrdDF_2,IPrint-2,IteSCF, EMax);
    double xEKA = 0.8928/0.2*EKA;
    double xEKB = 0.8928/0.2*EKB;
    xETot = ENuclear + eNucSolvnt_old + eSolvnt_old + E1 + EJ + xEKA + xEKB
            + EX + EC + E_EFP + ESolv + E_born + Edisp + Eairbed;
    //FileMan(FM_WRITE,FILE_ENERGY,FM_DP,1,1,FM_BEG,&xETot);
    //Added by Kaushik for libdh
    EKA = xEKA;
    EKB = xEKB;
  }

  if(rem_read(REM_LEVEXC) == XCFUNC_wB97M_2) { /* wB97M(2) functional */
    LOGICAL UseIntScreen = SCFConv.UseIntScreen();
    LOGICAL Use_dP       = SCFConv.Use_dP();
    double  VThresh      = SCFConv.VThresh();

    XCFunc = wB97M2();
    IGrdDF_2 = pick_grid(rem_read(REM_IGRDTY),EMax,IteSCF,NBasis);
    rem_write(pick_XC_thresh(IGrdDF_2!=rem_read(REM_IGRDTY),EMax,Cnverg),
                     REM_DFT_THRESH);
    DFTman(&EX,&EC,jXCAv,jXCBv,jPAv,jCAXC,NULL,NULL,2,
           XCFunc,IGrdDF_2,IPrint-2,IteSCF, EMax);

    IGrdDF_2 = pick_grid(rem_read(REM_NL_GRID),EMax,IteSCF,NBasis);
    rem_write(pick_XC_thresh(IGrdDF_2!=rem_read(REM_NL_GRID),EMax,Cnverg),
                     REM_DFT_THRESH);
    double Junk, ENLC;
    double *jNLAv, *jNLBv;
    jNLAv = QAllocDouble2(NB2car*NDen,shared);
    jNLBv = jNLAv + NB2car*(NDen-1);
    DFTman(&Junk,&ENLC,jNLAv,jNLBv,jPAv,jCAXC,NULL,NULL,1,
           XCFunctional(0,CFUNC_NL_Init),IGrdDF_2,IPrint-2,IteSCF,EMax);
    DFTman(&Junk,&ENLC,jNLAv,jNLBv,jPAv,jCAXC,NULL,NULL,2,
           XCFunctional(0,CFUNC_NL_Eval),IGrdDF_2,IPrint-2,IteSCF, EMax);
    printf(" Nonlocal correlation = %16.10f\n", ENLC);

    double *jxKA=NULL, *jxKB=NULL, *jxKAsr=NULL, *jxKBsr=NULL;
    jxKA = QAllocDouble2(NBas6D*NBas6D*NDen,shared);
    jxKB = jxKA + NBas6D*NBas6D*(NDen-1);
    jxKAsr = QAllocDouble2(NBas6D*NBas6D*NDen,shared);
    jxKBsr = jxKAsr + NBas6D*NBas6D*(NDen-1);

/*    double *jPAorig=NULL, *jPBorig=NULL;
    jPAorig = QAllocDouble2(NBas6D*NBas6D*NDen,shared);
    jPBorig = jPAorig + NBas6D*NBas6D*(NDen-1);
    VRcopy(jPAorig, jPA, NBas6D*NBas6D);
    if (NDen == 2) VRcopy(jPBorig, jPB, NBas6D*NBas6D);

    rem_write(OP_ERF,REM_INTEGRAL_2E_OPR);
    MakeK(jxKA,jxKB,jPAorig,jPBorig,IPrint-2,NDeriv,VThresh,UseIntScreen,Use_dP,XCFunc.KCof(),hfx_lr_coef);
    VRscale(jxKA,NBasis*NBasis,hfx_lr_coef);
    if (NDen == 2) VRscale(jxKB,NBasis*NBasis,hfx_lr_coef);
    rem_write(OP_ERFC,REM_INTEGRAL_2E_OPR);
    MakeK(jxKAsr,jxKBsr,jPAorig,jPBorig,IPrint-2,NDeriv,VThresh,UseIntScreen,Use_dP);
    VRscale(jxKAsr,NBasis*NBasis,XCFunc.KCof());
    if (NDen == 2) VRscale(jxKBsr,NBasis*NBasis,XCFunc.KCof());
    rem_write(OP_R12,REM_INTEGRAL_2E_OPR);

    double xEKA, xEKB, xEKAsr, xEKBsr;
    VRdot(&xEKA,jPAorig,jxKA,NBasis*NBasis);
    if (NDen == 2)
      VRdot(&xEKB,jPBorig,jxKB,NBasis*NBasis);
    else
      xEKB = xEKA;
    xEKA *= 0.5;
    xEKB *= 0.5;
    VRdot(&xEKAsr,jPAorig,jxKAsr,NBasis*NBasis);
    if (NDen == 2)
       VRdot(&xEKBsr,jPBorig,jxKBsr,NBasis*NBasis);
    else
       xEKBsr = xEKAsr;
    xEKAsr *= 0.5;
    xEKBsr *= 0.5;
    xEKA += xEKAsr;
    xEKB += xEKBsr;*/

    rem_write(OP_ERF,REM_INTEGRAL_2E_OPR);
    MakeK(jxKA,jxKB,jPA,jPB,IPrint-2,NDeriv,VThresh,UseIntScreen,Use_dP,XCFunc.KCof(),hfx_lr_coef);
    VRscale(jxKA,NBasis*NBasis,hfx_lr_coef);
    if (NDen == 2) VRscale(jxKB,NBasis*NBasis,hfx_lr_coef);
    rem_write(OP_ERFC,REM_INTEGRAL_2E_OPR);
    MakeK(jxKAsr,jxKBsr,jPA,jPB,IPrint-2,NDeriv,VThresh,UseIntScreen,Use_dP);
    VRscale(jxKAsr,NBasis*NBasis,XCFunc.KCof());
    if (NDen == 2) VRscale(jxKBsr,NBasis*NBasis,XCFunc.KCof());
    rem_write(OP_R12,REM_INTEGRAL_2E_OPR);

    double xEKA, xEKB, xEKAsr, xEKBsr;
    VRdot(&xEKA,jPA,jxKA,NBasis*NBasis);
    if (NDen == 2)
      VRdot(&xEKB,jPB,jxKB,NBasis*NBasis);
    else
      xEKB = xEKA;

    xEKA *= 0.5;
    xEKB *= 0.5;

    VRdot(&xEKAsr,jPA,jxKAsr,NBasis*NBasis);
    if (NDen == 2)
       VRdot(&xEKBsr,jPB,jxKBsr,NBasis*NBasis);
    else
       xEKBsr = xEKAsr;

    xEKAsr *= 0.5;
    xEKBsr *= 0.5;

    xEKA += xEKAsr;
    xEKB += xEKBsr;

    xETot = ENuclear+eNucSolvnt_old+eSolvnt_old+E1+EJ+xEKA+xEKB+EX+EC+ENLC+E_EFP+ESolv+E_born+Edisp+Eairbed;

    FileMan(FM_WRITE,FILE_ENERGY,FM_DP,1,FILE_POS_SCF_ENLC,FM_BEG,&ENLC);

    EKA = xEKA;
    EKB = xEKB;
    QFree(jxKA);
    QFree(jxKAsr);
    //QFree(jPAorig);
    //FileMan(FM_WRITE,FILE_ENERGY,FM_DP,1,1,FM_BEG,&xETot);
  }

  QTimerOff(t1,t0);  /* Time the SCF */

  if(rem_read(REM_LEVEXC) == XCFUNC_wB97M_OS ||
     rem_read(REM_LEVEXC) == XCFUNC_wB97M_OS_nSCF) { /* wB97M(OS) functional */
    LOGICAL UseIntScreen = SCFConv.UseIntScreen();
    LOGICAL Use_dP       = SCFConv.Use_dP();
    double  VThresh      = SCFConv.VThresh();
    XCFunc = wB97MOS();
    IGrdDF_2 = pick_grid(rem_read(REM_IGRDTY),EMax,IteSCF,NBasis);
    rem_write(pick_XC_thresh(IGrdDF_2!=rem_read(REM_IGRDTY),EMax,Cnverg),
                     REM_DFT_THRESH);
    DFTman(&EX,&EC,jXCAv,jXCBv,jPAv,jCAXC,NULL,NULL,2,
           XCFunc,IGrdDF_2,IPrint-2,IteSCF, EMax);
    IGrdDF_2 = pick_grid(rem_read(REM_NL_GRID),EMax,IteSCF,NBasis);
    rem_write(pick_XC_thresh(IGrdDF_2!=rem_read(REM_NL_GRID),EMax,Cnverg),
                     REM_DFT_THRESH);
    double Junk, ENLC;
    double *jNLAv, *jNLBv;
    jNLAv = QAllocDouble2(NB2car*NDen,shared);
    jNLBv = jNLAv + NB2car*(NDen-1);
    DFTman(&Junk,&ENLC,jNLAv,jNLBv,jPAv,jCAXC,NULL,NULL,1,
           XCFunctional(0,CFUNC_NL_Init),IGrdDF_2,IPrint-2,IteSCF,EMax);
    DFTman(&Junk,&ENLC,jNLAv,jNLBv,jPAv,jCAXC,NULL,NULL,2,
           XCFunctional(0,CFUNC_NL_Eval),IGrdDF_2,IPrint-2,IteSCF, EMax);
    printf(" Nonlocal correlation = %16.10f\n", ENLC);

    double *jxKA=NULL, *jxKB=NULL, *jxKAsr=NULL, *jxKBsr=NULL;
    jxKA = QAllocDouble2(NBas6D*NBas6D*NDen,shared);
    jxKB = jxKA + NBas6D*NBas6D*(NDen-1);
    jxKAsr = QAllocDouble2(NBas6D*NBas6D*NDen,shared);
    jxKBsr = jxKAsr + NBas6D*NBas6D*(NDen-1);

    rem_write(OP_ERF,REM_INTEGRAL_2E_OPR);
    MakeK(jxKA,jxKB,jPA,jPB,IPrint-2,NDeriv,VThresh,UseIntScreen,Use_dP,XCFunc.KCof(),hfx_lr_coef);
    VRscale(jxKA,NBasis*NBasis,hfx_lr_coef);
    if (NDen == 2) VRscale(jxKB,NBasis*NBasis,hfx_lr_coef);
    rem_write(OP_ERFC,REM_INTEGRAL_2E_OPR);
    MakeK(jxKAsr,jxKBsr,jPA,jPB,IPrint-2,NDeriv,VThresh,UseIntScreen,Use_dP);
    VRscale(jxKAsr,NBasis*NBasis,XCFunc.KCof());
    if (NDen == 2) VRscale(jxKBsr,NBasis*NBasis,XCFunc.KCof());
    rem_write(OP_R12,REM_INTEGRAL_2E_OPR);

    double xEKA, xEKB, xEKAsr, xEKBsr;
    VRdot(&xEKA,jPA,jxKA,NBasis*NBasis);
    if (NDen == 2)
      VRdot(&xEKB,jPB,jxKB,NBasis*NBasis);
    else
      xEKB = xEKA;

    xEKA *= 0.5;
    xEKB *= 0.5;

    VRdot(&xEKAsr,jPA,jxKAsr,NBasis*NBasis);
    if (NDen == 2)
       VRdot(&xEKBsr,jPB,jxKBsr,NBasis*NBasis);
    else
       xEKBsr = xEKAsr;

    xEKAsr *= 0.5;
    xEKBsr *= 0.5;

    xEKA += xEKAsr;
    xEKB += xEKBsr;

    xETot = ENuclear+eNucSolvnt_old+eSolvnt_old+E1+EJ+xEKA+xEKB+EX+EC+ENLC+E_EFP+ESolv+E_born+Edisp+Eairbed;

    FileMan(FM_WRITE,FILE_ENERGY,FM_DP,1,FILE_POS_SCF_ENLC,FM_BEG,&ENLC);

    EKA = xEKA;
    EKB = xEKB;
    QFree(jxKA);
    QFree(jxKAsr);
    //QFree(jPAorig);
    //FileMan(FM_WRITE,FILE_ENERGY,FM_DP,1,1,FM_BEG,&xETot);
  }


#ifdef RUSTY
  //RST: time scf
  QTimerOff(rusty11,rusty10);
  printf("TIMEINFO->: iterations %.2f sec.\n",rusty11[0]);
  // print SCF timing
  printf("TIMEINFO: SCF cpu time is %f sec.\n",t1[0]);
#endif

  if (rem_read(REM_CDFTCI_FRAGMENT)>0 && !rem_read(REM_HIRSHFELD_ACTIVE)) {
     rem_write(0,REM_CDFTCI_FRAGMENT);
     // keep ahold of converged promolecule density for later
     if (rem_read(REM_CDFT_POP) != -1) {
     FileMan(FM_WRITE,FILE_CDFT_HIRSHFELD_PROMOLECULE_DM,FM_DP,
             NBasis*NBasis,0,FM_BEG,jPA);
     if (NDen == 2)
         FileMan(FM_WRITE,FILE_CDFT_HIRSHFELD_PROMOLECULE_DM,FM_DP,
                 NBasis*NBasis,0,FM_CUR,jPB); // beta
    }
     cdftci_post_fragment(jPAv, IPrint, IteSCF, NBasis, N2, Cnverg,
                EMax, NDen, NB2car);
  }

  // Compute and Store Atomic Becke Weights
  if (rem_read(REM_CDFT_BECKE_POP) && rem_read(REM_CDFT) && !rem_read(REM_HIRSHFELD_ACTIVE)){
    int *iAtNo, NAtoms;
    get_carts(NULL,NULL,&iAtNo,&NAtoms);
    int* pseudodata = NULL;
    if (rem_read(REM_PSEUDOPOTENTIAL) > 0){
      pseudodata = new INTEGER[NELMTS+1];
      GetPseudoData(pseudodata);
    }
    double tmp1, tmp2;
    double *jCDFT_MatAv = QAllocDouble2(NB2car * NDen, shared);
    double *jCDFT_MatBv = jCDFT_MatAv + NB2car * (NDen - 1);
    IGrdDF_2 = pick_grid(rem_read(REM_IGRDTY),EMax,IteSCF,NBasis);
    XCFunctional XCFunc_CDFT(XFUNC_CDFT);
    LOGICAL INCDFT_TMP = rem_read(REM_INCDFT);
    rem_write(0, REM_INCDFT);
    INTEGER REDUCE_S2_TMP = rem_read(REM_REDUCE_S2);
    rem_write(0, REM_REDUCE_S2);
    rem_write(1,REM_CDFT_BECKE_POP_TMP);
    VRload(cdft_becke_count(),2*NAtoms,0.);
    DFTman(&tmp1, &tmp2, jCDFT_MatAv, jCDFT_MatBv, jPAv, NULL, NULL,
           NULL, 2, XCFunc_CDFT, IGrdDF_2, IPrint - 2, IteSCF, 0);
    rem_write(0,REM_CDFT_BECKE_POP_TMP);
    rem_write(INCDFT_TMP, REM_INCDFT);
    rem_write(REDUCE_S2_TMP, REM_REDUCE_S2);
    QFree(jCDFT_MatAv);
    double* beckearray = cdft_becke_count();
    for(int iAtom = 0; iAtom < NAtoms; iAtom++){
    for(int iDen = 0; iDen < NDen; iDen++){
        beckearray[iAtom + iDen*NAtoms] -= (double) iAtNo[iAtom]/NDen;
        if (rem_read(REM_PSEUDOPOTENTIAL) > 0)
            beckearray[iAtom + iDen*NAtoms] += (double) pseudodata[iAtNo[iAtom]]/NDen;
    }
    }
    delete [] pseudodata;
  }

if (jCDFT != NULL){    // Deallocate CDFT Stuff
    cdft_final(jCDFT->Lams); // and set Lams for Grad
    int nmat = rem_read(REM_CDFT);
    for(int ii=0; ii < nmat; ++ii) {
        printf(" Lam %20.16f\n", *(jCDFT->Lams + ii));
    }
    if (Converged && (rem_read(REM_CDFTCI) != 0))
    {
       cdftci_write_file(&ETot, jCDFT, NBasis, NOrb, NDen, jCA, jEA, NAlpha, jCB, jEB, NBeta);
    }
    delete jCDFT;
}

  // Free up IncFock stuff........

  if(SCFConv.UseIncFock()){
    QFree(jdPv),QFree(jdJv),QFree(jPvlast),QFree(jJvlast);
    if((XCFunc.HasHF() || add_LRK || LRC) || (dc_dft && XCFunc.IsPureDFT()) || (dscf_eda && XCFunc.IsPureDFT()))
    {
      QFree(jdPA),QFree(jPAlast);
      QFree(jdKA),QFree(jKAlast);
      if (XCFunc.HasHF() && LRC){
         QFree(jdKAsr); QFree(jKAsrLast);
      }
    }
  }

  // If long-range exchange was added, we should free the automatically allocated integral
  // interpolation tables, unless we will do a CIS/RPA. (TD 2/06)
  if (add_LRK && !rem_read(REM_SET_ROOTS)) {GmnTab_free();}

  // Place a copy of the Fock matrices in the proper place on disk

  if (jFA == NULL) {
    jFA = QAllocDouble(N2*NDen);
    jFB = jFA + N2*(NDen-1);
  }


  FileMan_Open_Read(FILE_TEMP_FOCK);
  FileMan(FM_READ,FILE_TEMP_FOCK,FM_DP,N2*NDen,0,FM_BEG,jFA);
  FileMan_Close(FILE_TEMP_FOCK);

// BJA_FIX : Fix and Write Fock Matrix for Post-HF calcs

  if (rem_read(REM_EMBED_INTERNAL)) {

      if (IPrint >= 2) {
        MatPrint(jFA, NBasis, NBasis, "jFA Final");
        if (NDen == 2) MatPrint(jFB, NBasis, NBasis, "jFB Final");
      }
      mufact = -mufact;
      VRscale(jProjOpA, N2, mufact);
      VRadd(jFA, jProjOpA, jFA, N2);
      if (IPrint >= 2) {
        MatPrint(jProjOpA, NBasis, NBasis, "-mu*jProjOpA");
        MatPrint(jFA, NBasis, NBasis, "jFA Final - mu*jProjOpA");
        if (NDen == 2) {MatPrint(jFB, NBasis, NBasis, "jFB Final - mu*jProjOpA");}
      }
      VRscale(jProjOpA, N2, -1.0 / mufact);

      // Symmetrize Fock Matrix to alleviate numerical errors

      double * jEF = QAllocDoubleWithInit(N2);

      GenMatrix EmbedFock(jEF, N, N);
      VRcopy(jEF, jFA, N2);
      EmbedFock.Symmetrize();
      VRcopy(jFA, jEF, N2);
      VRcopy(jFB, jEF, N2);
  }

  //BJA_FREE
  if (rem_read(REM_EMBED_INTERNAL)) {
    QFree(jPAfrg2);
    QFree(jPAfrg2v);
    QFree(jPAfrg12);
    QFree(jPAfrg12v);
    QFree(jPBfrg2);
    QFree(jPBfrg2v);
    QFree(jPBfrg12);
    QFree(jPBfrg12v);
    QFree(jPAoriginal);
    QFree(jProjOpA);
    QFree(jProjOpAv);
  }

  //KCF unconstrain Fock for proper MO energies
  // NOTE: The step(...) routine will also write unconstrained eigenvalues to disk
  if( rem_read(REM_STEP) == 1 )
  {
      if(jCA == NULL)
      {
        jCA = QAllocDouble(NDen*NOrb*NBasis);
        jCB = jCA + (NDen-1)*NOrb*NBasis;
        FileMan(FM_READ,FILE_MO_COEFS,FM_DP,NDen*NOrb*NBasis,0,FM_BEG,jCA);
      }
        step(jFA,jCA,jS,eta_A,eta_B,NAlpha,NBasis,NOrb,IteSCF,true,false,step_always_alpha);
        if( NDen == 2 )
            step(jFB,jCB,jS,eta_A,eta_B,NBeta,NBasis,NOrb,IteSCF,false,false,step_always_beta);
        // copy fock back over
        ScaV2M(jFA,jFAv,True,False);
        if(NDen == 2) ScaV2M(jFB,jFBv,True,False);
        // free the things
        QFree(jCA);
  }

  FileMan_Open_Write(FILE_FOCK_MATRIX);
  FileMan(FM_WRITE,FILE_FOCK_MATRIX,FM_DP,N*N,0,FM_BEG,jFA);
  FileMan(FM_WRITE,FILE_FOCK_MATRIX,FM_DP,N*N,0,FM_CUR,jFB);
  FileMan_Close(FILE_FOCK_MATRIX);

  if ((dc_dft && have_dftE) || (dscf_eda && have_dftE))
  {  //cout << "JMH: DC_FileSave call #5 (todo=2)\n";
     DC_FileSave(2,NBasis,NDen,NB2,NOrb,N2,jFA,jFB,NULL);
  }

  if(rem_opsing == 1)
  { // NAB for open-shell singlet method
     if(rem_read(REM_TRIPLET) == 1)
     {
        FileMan_Open_Write(FILE_FOCK_T_MATRIX);
        FileMan(FM_WRITE,FILE_FOCK_T_MATRIX,FM_DP,N*N,0,FM_BEG,jFA);
        FileMan(FM_WRITE,FILE_FOCK_T_MATRIX,FM_DP,N*N,0,FM_CUR,jFB);
        FileMan_Close(FILE_FOCK_T_MATRIX);
     }else{
        FileMan_Open_Write(FILE_FOCK_S_MATRIX);
        FileMan(FM_WRITE,FILE_FOCK_S_MATRIX,FM_DP,N*N,0,FM_BEG,jFA);
        FileMan(FM_WRITE,FILE_FOCK_S_MATRIX,FM_DP,N*N,0,FM_CUR,jFB);
        FileMan_Close(FILE_FOCK_S_MATRIX);
     }
  }

  if (do_efp)
  {
	EFP2::instance().compute(0);
	ETot += EFP2::instance().get_total_energy() - E_EFP;

    // LVS commented this out
	//double EFPNucEnergy;
	//FileMan(FM_READ, FILE_ENERGY,FM_DP,1,FILE_POS_NUC_REPUL_ENERGY,FM_BEG,&EFPNucEnergy);
	//EFPNucEnergy += EFP2::instance().get_total_energy() - E_EFP;
	//FileMan(FM_WRITE,FILE_ENERGY,FM_DP,1,FILE_POS_NUC_REPUL_ENERGY,FM_BEG,&EFPNucEnergy);
  }

 // LDJ - XPOL
  if (isXPol && rem_read(REM_MP2_RESTART_NO_SCF) != 1)
  {
     //write gas phase fock matrix as well
     double *jFgas = QAllocDouble(2*N*N);
     VRcopy(jFgas,jFA,N*N);
     VRcopy(&jFgas[N*N],jFB,N*N);
     INTEGER currFrag = xpolCurrFrag();
     double *jXPOLv = QAllocDouble(NB2);
     double *jXPOL = QAllocDouble(N*N);
     FileMan(FM_READ,FILE_XPOL_ES_INTERACTION_MATRIX,FM_DP,NB2,0,FM_BEG,jXPOLv);
     ScaV2M(jXPOL,jXPOLv,1,1);
     VRscale(jXPOL,N*N,-1.0);
     VRadd(jFgas,jXPOL,N*N);
     VRadd(&jFgas[N*N],jXPOL,N*N);
     FileMan(FM_READ,FILE_XPOL_MIN_INTERACTION_MATRIX,FM_DP,NB2,0,FM_BEG,jXPOLv);
     ScaV2M(jXPOL,jXPOLv,1,1);
     VRscale(jXPOL,N*N,-1.0);
     VRadd(jFgas,jXPOL,N*N);
     VRadd(&jFgas[N*N],jXPOL,N*N);
     FileMan(FM_WRITE,FILE_FOCK_MATRIX_GAS,FM_DP,2*N*N,0,FM_BEG,jFgas);

     // XPol 0th-order energies.  This is Eq. (3) of JCP 134, 094118 (2011)
     double EXPOL0 = ETot + xpMinE - xpNucMull;
#ifdef DEVELOPMENT
     //printf("XPol Etot = %16.8f\n",ETot); // same as SCF energy
     printf(" XPol elst embedding energy = %12.8f a.u. = %7.3f kcal/mol\n",
          xpNucMull-xpMinE, (xpNucMull-xpMinE)*au2kcal);
#endif
     FileMan(FM_WRITE,FILE_XPOL_E0,FM_DP,1,currFrag,FM_BEG,&EXPOL0);
     // total electrostatic energy for this fragment
     double xpES = xpNucMull + xpElecMull;
     FileMan(FM_WRITE,FILE_XPOL_FRAG_ES,FM_DP,1,currFrag,FM_BEG,&xpES);
     QFree(jXPOLv);
     QFree(jXPOL);
     QFree(jFgas);
  }


  //AIK: need this for reading orbitals from another job
  if (Converged || NoSCF) 
  {

    FileMan(FM_WRITE,FILE_ENERGY,FM_DP,1,FILE_POS_SCF_ENERGY,FM_BEG,&ETot);
    ef.save(ef.energy, ETot);
    --IteSCF;
    Comment = " Convergence criterion met";
    if (dc_dft) Comment = "      DC-DFT energy using HF orbitals";
    if (IteSCF == 1) {
      if(SCFConv.doingSVP()){
	printf(" -------------------------------------------------------\n");
	if (usingGDM || usingDM)
	  printf("  Cycle       Energy        RMS Gradient   SVP Error\n");
	  else if(usingNEGF)
	    printf("  Cycle       Energy         NEGF Error\n");
	else
	  printf("  Cycle       Energy         DIIS Error    SVP Error\n");
	printf(" -------------------------------------------------------\n");
      }
      else {
	printf(" ---------------------------------------\n");
	if (usingGDM || usingDM || usingGDIIS)
	  printf("  Cycle       Energy        RMS Gradient\n");
        else
	  printf("  Cycle       Energy         DIIS Error\n");
	printf(" ---------------------------------------\n");
      }
    }



#ifdef DEVELOPMENT
    if(SCFConv.doingSVP())
      printf("%5d%19.10lf%14.2E%14.2E     00000",IteSCF,ETot,EMax,SVP_Error);
    else if (dc_dft)
      printf("%5d%19.10lf  00000",IteSCF,ETot);
    else
      printf("%5d%19.10lf%14.2E  00000",IteSCF,ETot,EMax);
#else
    if(SCFConv.doingSVP())
      printf("%5d%19.10lf%14.2E%14.2E",IteSCF,ETot,EMax,SVP_Error);
    else if (dc_dft)
      printf("%5d%19.10lf",IteSCF,ETot);
    else
      printf("%5d%19.10lf%14.2E",IteSCF,ETot,EMax);
#endif
    // EPIF - Need to use printf, not cout, to avoid an i/o bug
    if(!rem_read(REM_HIRSHFELD_ACTIVE)) printf("%s", Comment.c_str());
    printf("\n");
    if(SCFConv.doingSVP())
      printf(" -------------------------------------------------------\n");
    else
      printf(" ---------------------------------------\n");

    // igor/ysj
    if(rem_read(REM_LEVEXC) == XCFUNC_XYG3 || rem_read(REM_LEVEXC) == XCFUNC_XYG3RI) { /* XYG3 functional */
      cout << " B3LYP orbitals are now ready for the XYG3 calculation." << endl;
      cout << " XYG3 energy = Exch (0.8033 HF  - 0.0140 Slater + 0.2107 Becke88) + " << endl;
      cout << "               Corr (0.6789 LYP + 0.3211 MP2)" << endl;
      ETot = xETot;
    }
    if(rem_read(REM_LEVEXC) == XCFUNC_XYGJOS || rem_read(REM_LEVEXC) == XCFUNC_LXYGJOS) { /* XYGJOS functional */
      cout << " B3LYP orbitals are now ready for the XYGJ-OS calculation." << endl;
      cout << " XYGJ-OS energy = Exch (0.7731 HF  + 0.2269 Slater) + " << endl;
      cout << "                  Corr (0.2754 LYP + 0.2309 VWN1RPA + 0.4364 OS-MP2)" << endl;
      ETot = xETot;
    }
    if(rem_read(REM_LEVEXC) == XCFUNC_XYG_OS5) { /* XYG_OS5 functional */
      cout << " B3LYP orbitals are now ready for the XYG-OS5 calculation." << endl;
      cout << " XYG-OS5 energy = Exch (0.8928 HF  + 0.3393 Slater - 0.2321 Becke88) + " << endl;
      cout << "                  Corr (-0.0635 LYP + 0.3268 VWN1RPA + 0.5574 OS-MP2)" << endl;
      ETot = xETot;
    }

    if(rem_read(REM_LEVEXC) == XCFUNC_wB97M_2) { /* wB97M(2) functional */
      cout << " wB97M-V orbitals are now ready for the wB97M(2) calculation." << endl;
      cout << " wB97M(2) energy = Exch (0.62194 SRHF + 1.0 LRHF + wB97M(2)_EXCH) + " << endl;
      cout << "               Corr (wB97M(2)_CORR + 0.34096 MP2 + 0.65904 VV10(b=10))" << endl;
      ETot = xETot;
    }

    if(rem_read(REM_LEVEXC) == XCFUNC_wB97M_OS ||
       rem_read(REM_LEVEXC) == XCFUNC_wB97M_OS_nSCF) { /* wB97M(OS) functional */
      cout << " wB97M-V orbitals are now ready for the wB97M(OS) calculation." << endl;
      cout << " wB97M(OS) energy = Exch (0.50034 SRHF + 1.0 LRHF + wB97M(OS)_EXCH) + " << endl;
      cout << "               Corr (wB97M(OS)_CORR + 0.45340 opposite-spin MP2 + 1.04880 VV10(b=10))" << endl;
      ETot = xETot;
    }

    // Jaehoon
    if(rem_read(REM_LEVEXC) == XCFUNC_QACFRI) { /* QACF functional */
      cout << " Becke's half-and-half orbitals are now ready for the QACF calculation." << endl;
      cout << " QACF energy = Exch (0.6666 HF  + 0.3333 PBEx) + " << endl;
      cout << "               Corr (0.3333 PBE-potential-correlation + 0.3333 MP2)" << endl;
      ETot = xETot;
    }

    //
    // XDM for DFT ( perturbative )
    //     we only need correct density jPAv and XCFunc
    if ( vdwJob == 1 &&  ( Converged || (IteSCF == MaxSCF) ) )
    {
       // JMH:  why is w_GDD inside of the vdwJob scope?

       // reset vdwdata->vdwJob
       vdwdata->vdwJob=1;

       XCFunctional XCFuncN;
       XCFuncN.AddC(CFUNC_VDW_BR89,1.0);
       XCFuncN.setType();

       if(rem_read(REM_OMEGA_GDD) == 1)
       {
          printf("\n\n    === Starting w_GDD tuning === \n");
       }
       else{ // XDM
         printf(" Exchange    energy = %16.10f a.u.\n",EX);
         printf(" Correlation energy = %16.10f a.u.\n",EC);
         printf("\n\n");
         printf(" --------------------------------- \n");
         printf("    Starting XDM module in DFT     \n");
         printf(" --------------------------------- \n\n");
       }

       //turn off new BLAS3 DFT method for VDW
       int newdft = rem_read(REM_NEW_DFT);
       if ( newdft != 0 ) rem_write(0, REM_NEW_DFT);

       // JMH: this looks like an ugly hack where the wGDD code is somehow piggy-backing off the
       // (unrelated) DFT-vdW / XDM code.  Would be nice to move wGDD to its own subroutine.
       double ECXDM=0;
       double EXXDM=0;
       double* jXCAv_t=new double[NB2car*NDen];
       for (int i=0;i<NB2car*NDen;i++) { jXCAv_t[i]=0.; }
       double* jXCBV_t = jXCAv_t+ NB2car*(NDen-1);
       DFTman(&EXXDM,&ECXDM,jXCAv,jXCBv,jPAv,jCAXC,NULL,NULL,2,
              XCFuncN,IGrdDF_2,IPrint-2,IteSCF, EMax);
       if(rem_read(REM_OMEGA_GDD) == 1){
         int NorInt = rem_read(REM_OMEGA_GDD_N);
         int omega_gdd = rem_read(REM_OMEGA_GDD_VALUE);
         int mu_tmp = rem_read(REM_OMEGA_GDD_MU);
         cout << "Mu = " << mu_tmp << " ; normalization integral = "
              << NorInt << " ; omega_GDD = " << omega_gdd << endl;
        // mu - 50 until we can scan a smaller window
        if(NorInt > 10000){
           do{
             mu_tmp = rem_read(REM_OMEGA_GDD_MU);
             if(mu_tmp == 50) break;
             mu_tmp = mu_tmp - 50;
             rem_write(mu_tmp,REM_OMEGA_GDD_MU);
             for (int i=0;i<NB2car*NDen;i++) { jXCAv_t[i]=0.; }
             DFTman(&EXXDM,&ECXDM,jXCAv,jXCBv,jPAv,jCAXC,NULL,NULL,2,
                    XCFuncN,IGrdDF_2,IPrint-2,IteSCF, EMax);
             NorInt = rem_read(REM_OMEGA_GDD_N);
             omega_gdd = rem_read(REM_OMEGA_GDD_VALUE);
             cout << "Mu = " << mu_tmp << " ; normalization integral = "
                  << NorInt << " ; omega_GDD = " << omega_gdd << endl;
           }while(NorInt > 10000);
         }
         // mu +- 5
         if(NorInt > 1000){
           do{
             mu_tmp = rem_read(REM_OMEGA_GDD_MU);
             mu_tmp = mu_tmp - 5;
             rem_write(mu_tmp,REM_OMEGA_GDD_MU);
             for (int i=0;i<NB2car*NDen;i++) { jXCAv_t[i]=0.; }
             DFTman(&EXXDM,&ECXDM,jXCAv,jXCBv,jPAv,jCAXC,NULL,NULL,2,
                    XCFuncN,IGrdDF_2,IPrint-2,IteSCF, EMax);
             NorInt = rem_read(REM_OMEGA_GDD_N);
             omega_gdd = rem_read(REM_OMEGA_GDD_VALUE);
             cout << "Mu = " << mu_tmp << " ; normalization integral = "
                  << NorInt << " ; omega_GDD = " << omega_gdd << endl;
           }while(NorInt > 1000);
         }
         else if(NorInt < 1000){
           do{
             mu_tmp = rem_read(REM_OMEGA_GDD_MU);
             mu_tmp = mu_tmp + 5;
             rem_write(mu_tmp,REM_OMEGA_GDD_MU);
             for (int i=0;i<NB2car*NDen;i++) { jXCAv_t[i]=0.; }
             DFTman(&EXXDM,&ECXDM,jXCAv,jXCBv,jPAv,jCAXC,NULL,NULL,2,
                   XCFuncN,IGrdDF_2,IPrint-2,IteSCF, EMax);
             NorInt = rem_read(REM_OMEGA_GDD_N);
             omega_gdd = rem_read(REM_OMEGA_GDD_VALUE);
             cout << "Mu = " << mu_tmp << " ; normalization integral = "
                  << NorInt << " ; omega_GDD = " << omega_gdd << endl;
           }while(NorInt < 1000);
         }
         // mu +- 1
         if(NorInt > 1000)
         {
           do{
             mu_tmp = rem_read(REM_OMEGA_GDD_MU);
             mu_tmp = mu_tmp - 1;
             rem_write(mu_tmp,REM_OMEGA_GDD_MU);
             for (int i=0;i<NB2car*NDen;i++) { jXCAv_t[i]=0.; }
             DFTman(&EXXDM,&ECXDM,jXCAv,jXCBv,jPAv,jCAXC,NULL,NULL,2,
                   XCFuncN,IGrdDF_2,IPrint-2,IteSCF, EMax);
             NorInt = rem_read(REM_OMEGA_GDD_N);
             omega_gdd = rem_read(REM_OMEGA_GDD_VALUE);
             cout << "Mu = " << mu_tmp << " ; normalization integral = "
                  << NorInt << " ; omega_GDD = " << omega_gdd << endl;
           }while(NorInt > 1000);
         }
         else if(NorInt < 1000){
           do{
             mu_tmp = rem_read(REM_OMEGA_GDD_MU);
             mu_tmp = mu_tmp + 1;
             rem_write(mu_tmp,REM_OMEGA_GDD_MU);
             for (int i=0;i<NB2car*NDen;i++) { jXCAv_t[i]=0.; }
             DFTman(&EXXDM,&ECXDM,jXCAv,jXCBv,jPAv,jCAXC,NULL,NULL,2,
                    XCFuncN,IGrdDF_2,IPrint-2,IteSCF, EMax);
             NorInt = rem_read(REM_OMEGA_GDD_N);
             omega_gdd = rem_read(REM_OMEGA_GDD_VALUE);
             cout << "Mu = " << mu_tmp << " ; normalization integral = "
                  << NorInt << " ; omega_GDD = " << omega_gdd << endl;
           }while(NorInt < 1000);
         }
         int NorInt_diff = abs(NorInt - 1000);
         // add and sub
	 int mu_tmp_add = rem_read(REM_OMEGA_GDD_MU);
         mu_tmp_add = mu_tmp_add + 1;
         int mu_tmp_sub = rem_read(REM_OMEGA_GDD_MU);
         mu_tmp_sub = mu_tmp_sub - 1;
         // add
         rem_write(mu_tmp_add,REM_OMEGA_GDD_MU);
         for (int i=0;i<NB2car*NDen;i++) { jXCAv_t[i]=0.; }
         DFTman(&EXXDM,&ECXDM,jXCAv,jXCBv,jPAv,jCAXC,NULL,NULL,2,
               XCFuncN,IGrdDF_2,IPrint-2,IteSCF, EMax);
         int NorInt_add = rem_read(REM_OMEGA_GDD_N);
         int omega_gdd_add = rem_read(REM_OMEGA_GDD_VALUE);
         int NorInt_diff_add = abs(NorInt_add - 1000);
         // sub
         rem_write(mu_tmp_sub,REM_OMEGA_GDD_MU);
         for (int i=0;i<NB2car*NDen;i++) { jXCAv_t[i]=0.; }
         DFTman(&EXXDM,&ECXDM,jXCAv,jXCBv,jPAv,jCAXC,NULL,NULL,2,
                XCFuncN,IGrdDF_2,IPrint-2,IteSCF, EMax);
         int NorInt_sub = rem_read(REM_OMEGA_GDD_N);
         int omega_gdd_sub = rem_read(REM_OMEGA_GDD_VALUE);
         int NorInt_diff_sub = abs(NorInt_sub - 1000);
         int omega_gdd_final = omega_gdd;
         if (NorInt_diff > NorInt_diff_add) omega_gdd_final = omega_gdd_add;
         if (NorInt_diff > NorInt_diff_sub) omega_gdd_final = omega_gdd_sub;
         printf("\t\t******************************************************************\n");
         printf("\t\t******************************************************************\n");
         printf("\t\t**   Tuning based on GDD scheme: w = ( %d / 1000 ) bohr^(-1)   **\n",
                omega_gdd_final);
         
         if (rem_read(REM_OMEGA_EFF) == 1) {
             double omega_eff = rem_read(REM_OMEGA_EFF_VALUE);
             printf("\t\t**   Density–erf omega (ω_eff): %10.6f bohr^(-1)              **\n",
                    omega_eff);
         }
         
         if (rem_read(REM_SET_ROOTS) > 0)
         {  // JMH (12/2025), tk #3690
            printf("\t\t**   NOTE: w = %.3f a.u. value has not been reset              **\n",
                0.001*(double)rem_read(REM_OMEGA));
         }
         printf("\t\t******************************************************************\n");

       }
       delete[] jXCAv_t;

       //restore back new BLAS3 DFT if needed
       rem_write(newdft, REM_NEW_DFT);

       if(rem_read(REM_OMEGA_GDD) != 1){
         printf(" XDM vdW energy = %16.10f a.u. \n", EXXDM+ECXDM);
       }
       EX += EXXDM; EC += ECXDM;
       if(rem_read(REM_OMEGA_GDD) != 1){
         printf(" Exchange    energy (final, with vdW) = %16.10f a.u.\n",EX);
         printf(" Correlation energy (final, with vdW) = %16.10f a.u.\n",EC);
       }
       ETot = ENuclear+eNucSolvnt_old+eSolvnt_old+E1+EJ+EKA+EKB+EX+EC+E_EFP+ESolv+E_born+Edisp;
       if(rem_read(REM_OMEGA_GDD) != 1){
         printf("%5d%19.10lf%14.2E -- (with XDM)\n\n",IteSCF,ETot,EMax);
       }
    }


    //AML,RDA
    /* libdh reads FILE_ENERGY SCF components: always persist them for double
     * hybrids, even when SCF_FINAL_PRINT/IPrint gates would skip the block. */
    const LOGICAL write_dh_energy_components =
        (rem_read(REM_DH) != 0) || IsDoubleHybrid();
    if (DecompJ || IPrint >= 1 || rem_read(REM_SCF_FINAL_PRINT) >= 1 ||
        IsDoubleHybrid()) {

      if (!IsDoubleHybrid()) {
        if(rem_read(REM_TAO_DFT)>0) {
          printf(" Minus  Theta * Entropy = %16.10f\n",EtsA + EtsB);
        }
        printf(" One-Electron    Energy = %16.10f\n"
        " Total Coulomb   Energy = %16.10f\n"
        " Alpha Exchange  Energy = %16.10f\n"
        " Beta  Exchange  Energy = %16.10f\n"
        " DFT   Exchange  Energy = %16.10f\n"
        " DFT Correlation Energy = %16.10f\n"
              " Nuclear Repu.   Energy = %16.10f\n"
        " Nuclear Attr.   Energy = %16.10f\n"
        " Kinetic         Energy = %16.10f\n",
        E1,EJ,EKA,EKB,EX,EC,ENuclear,EV,E1-EV);
        if (DecompJ) printf(" Coulombic       Energy = %16.10f\n",ECou);
      }
      FileMan(FM_WRITE,FILE_ENERGY,FM_DP,1,FILE_POS_SCF_E1,FM_BEG,&E1);
      FileMan(FM_WRITE,FILE_ENERGY,FM_DP,1,FILE_POS_SCF_EJ,FM_BEG,&EJ);
      FileMan(FM_WRITE,FILE_ENERGY,FM_DP,1,FILE_POS_SCF_EKA,FM_BEG,&EKA);
      FileMan(FM_WRITE,FILE_ENERGY,FM_DP,1,FILE_POS_SCF_EKB,FM_BEG,&EKB);
      FileMan(FM_WRITE,FILE_ENERGY,FM_DP,1,FILE_POS_SCF_EX,FM_BEG,&EX);
      FileMan(FM_WRITE,FILE_ENERGY,FM_DP,1,FILE_POS_SCF_EC,FM_BEG,&EC);
      FileMan(FM_WRITE,FILE_ENERGY,FM_DP,1,FILE_POS_NUC_REPUL_ENERGY,FM_BEG,&ENuclear);
      FileMan(FM_WRITE,FILE_ENERGY,FM_DP,1,FILE_POS_SCF_EV,FM_BEG,&EV);
      //FileMan(FM_WRITE,FILE_ENERGY,FM_DP,1,FILE_POS_SCF_EC_NLC,FM_BEG,&ENLC);
      // Do not seed FILE_POS_PT2_CORRELATION_E here for wB97M(OS):
      // field-job fallback MP2/RIMP2 writers must remain authoritative.

    }
    // TT <EX|GS> overlap
    if (rem_read(REM_ROKS)>0)
      roks_overlap(jC0,jCA);
    if(SCFConv.doingSVP()){
      svp_finish();	// get SVPPunch in order to run DEFESR in SVPInfo
      svpinfo.Set_Energies(ETot);
      svpinfo.Set_Properties();
      svpinfo.Print();
      //svp_finish();
      hondoend();
    }
    if(usePCM && rem_read(REM_SMD_PCM) != 1 && !dofRF)
    {
       //final_pcm_print(jE_PCM, ETot);
       scrf::instance().final_print(NULL,ETot);
       if(jE_PCM != NULL) QFree(jE_PCM);
    }
    if(dofRF){
        double ES_RF_interaction = 0.0 ;
        int state_number = rem_read(REM_PCM_EQSTATE) ;
        FileMan(FM_READ,FILE_ES_RF_INTERACTION,FM_DP,1,state_number,FM_BEG,&ES_RF_interaction);

        cout << endl
             << "0====(SCF calculation in frozen reaction field finished)====0" << endl ;
        cout << setprecision(6) << "| SCF-fRF interaction energy =   " << jE_PCM[0]*au2eV
                         << " eV               |" << endl ;
        cout << setprecision(6) << "| Ref-fRF interaction energy =   " << ES_RF_interaction*au2eV
                         << " eV (state " << state_number << ")     |" << endl ;
        cout << "0===========================================================0" << endl << endl ;

     //Write interaction energy of SCF Dens with ASC to Disk for later use
     FileMan(FM_WRITE,FILE_ES_RF_INTERACTION,FM_DP,1,100,FM_BEG,&jE_PCM[0]);
     //cout << "### Wrote SCF-RF interaction (" << jE_PCM[0]*au2eV << " eV) to disk" << endl << endl ;

     QFree(jE_PCM);
     }

    // Print the <S^2> expectation value for unrestricted calculations

    if (JustAl == 1 && !hasFracElec) {
      double S2 = ExpecS2SCF();
      printf(" <S^2> = %.4f\n",S2);
    }
    // Print Becke Populations
    if (rem_read(REM_CDFT_BECKE_POP) && rem_read(REM_CDFT)
        || rem_read(REM_CDFT_POP) == BECKE && rem_read(REM_CDFT)){
      int *iAtNo, NAtoms;
      get_carts(NULL,NULL,&iAtNo,&NAtoms);
        double* beckearray = cdft_becke_count();
        printf("\n%40s\n","CDFT Becke Populations");
        printf("%52s\n",  "----------------------------------------------------");
        if(NDen == 1)
            printf("%16s%22s%22s%12s\n","Atom","Excess Electrons","Population (a.u.)","");
        else
            printf("%16s%22s%22s%12s\n","Atom","Excess Electrons","Population (a.u.)","Net Spin");
        for(int iAtom = 0; iAtom < NAtoms; iAtom++){
            if(NDen == 1) {
            double x=beckearray[iAtom];
            printf("%8i%8s%16.6f%16.6f\n",
                    iAtom + 1,
                    (char*)AtomicSymbol(iAtNo[iAtom]),x,x+iAtNo[iAtom]);
            }
            else {
            double x=beckearray[iAtom]+beckearray[iAtom+NAtoms];
            double y=beckearray[iAtom]-beckearray[iAtom+NAtoms];
            printf("%8i%8s%16.6f%16.6f%18.6f\n",
                    iAtom + 1,
                    (char*)AtomicSymbol(iAtNo[iAtom]),x,x+iAtNo[iAtom],y);
        }
        }
        printf("%52s\n\n","----------------------------------------------------");
    }
    // Print Hirshfeld Fragment Populations
    if (rem_read(REM_CDFT_POP) == FBH && rem_read(REM_CDFT))
    {
        int *iAtNo, NAtoms;
        get_carts(NULL,NULL,&iAtNo,&NAtoms);
        int NFrag = rem_read(REM_FRAGMENTS);
        // KCF -- again, simpler way to do this than I/O
        arma::ivec NAtomFrgm = arma::ivec(NFrag);
        frgmatoms(NFrag, NAtomFrgm);
        double Pops[NFrag];
        double FragTot[NFrag];
        double CTA_diff[NFrag];
        FileMan(FM_READ,FILE_HIRSHFELD_POPS,FM_DP,NFrag,0,FM_BEG,&Pops);
        int cAtom = 0; // current atom pointer
        int fAtom = 0; // final atom in fragment pointer
        for (int iFrag = 0; iFrag < NFrag; iFrag++){
            fAtom += NAtomFrgm(iFrag);//nAtsInFrag[iFrag];
            for (int iAtom = cAtom; iAtom < fAtom; iAtom++){
                FragTot[iFrag] += iAtNo[iAtom];
            }
            cAtom += NAtomFrgm(iFrag);//nAtsInFrag[iFrag];
            FragTot[iFrag] -= (Pops[iFrag]); // total fragment charge
        }

        printf("\n%40s\n","CDFT Hirshfeld Populations");
        printf("%40s\n",  "----------------------------------------");

        printf("%16s%12s%12s\n","Fragment","Net Charge","");
        for (int i = 0; i < NFrag; i++){
            printf("%8i%6s%12.6f\n",
                    i + 1,"", FragTot[i]);
        }
        printf("%32s\n","----------------------------------------");
    }

//NAB:Kohn-Sham DFT based XES

    if(rem_read(REM_NCORE_XES) >= 1){
          coretrans(jCA,jCB,jEA,jEB,NAlpha,NBeta,NBasis,NMO);
       }


    printf(" SCF time:  CPU %.2f s  wall %.2f s\n",t1[0],t1[2]);
    // save time for predicting Anharmonic correction time. Leaf
    // print out at the end of Freq calculation.
    FileMan(FM_WRITE,FILE_SCF_TIME,FM_DP,1,0,FM_BEG,&t1);


    if(rem_opsing == 1 && rem_read(REM_TRIPLET) == 1) 
    { // NAB work out corrected singlet energy
       printf("\n--- Corrected Open Shell Singlet Energy ---\n\n");
       printf("\n    Singlet energy = %22.13f\n", ESing);
       printf("    Triplet energy = %22.13f\n", ETot);
       EOpSing = 2*ESing-ETot;
       printf("    Open-shell singlet energy = %22.13f\n\n", EOpSing);
       FileMan(FM_WRITE,FILE_ENERGY,FM_DP,1,FILE_POS_CRNT_TOTAL_ENERGY,FM_BEG,&EOpSing);
       FileMan(FM_WRITE,FILE_ENERGY,FM_DP,1,FILE_POS_SCF_ENERGY,       FM_BEG,&EOpSing);
       ETot = EOpSing;
       rem_write(1,REM_FIRSTSCF);
    }

    t[0] = ETot;
    t[1] = E1;
    t[2] = EJ;
    t[3] = EKA;
    t[4] = EKB;
    t[5] = EX;
    t[6] = EC;
    ET = E1 - EV; // AML
    t[7] = ET;
    t[8] = ENuclear;
    t[9] = EV;

    FileMan(FM_WRITE,FILE_ENERGY,FM_DP,10,1,FM_BEG,t);

    if (rem_read(REM_QM_MM_INTERFACE) < 0) {
       FileMan(FM_WRITE,FILE_ENERGY,FM_DP,1,FILE_POS_CRNT_TOTAL_ENERGY,FM_BEG,&ETot);
    }
    else {
       printf(" E(QM + QM/MM): %19.10f", ETot);
       double Eold;
       FileMan(FM_READ,FILE_ENERGY,FM_DP,1,FILE_POS_MM_ENERGY,FM_BEG,&Eold);
       ETot += Eold;
       FileMan(FM_WRITE,FILE_ENERGY,FM_DP,1,FILE_POS_CRNT_TOTAL_ENERGY,FM_BEG,&ETot);
       //printf(" Eold: %12.7f E_qmmm: %17.12f \n", Eold, ETot);
       // ZQY -- not sure if Eold here is exactly equalt to E(MM)
       printf(" E(MM): %12.7f E(Tot): %17.12f \n", Eold, ETot);
       // AWL -- Also write to SCF energy
       FileMan(FM_WRITE,FILE_ENERGY,FM_DP,1,FILE_POS_SCF_ENERGY,FM_BEG,&ETot);
       FileMan(FM_WRITE,FILE_ENERGY,FM_DP,1,FILE_POS_EWALD_ENERGY,FM_BEG,&EewQMMM);
    }

  if (cosmo) 
  {
     scrf::instance().final_print(jPAv,ETot);
    /*
     INTEGER Three = 3;
     printf("before final oc correction, ETot: %20.10f\n", ETot);
     qchem_cosmo(&Three, jHv_cosmo, &ETot, jPAv);
     printf("SCF energy after oc correction: %20.10f\n", ETot);
     FileMan(FM_WRITE,FILE_ENERGY,FM_DP,1,FILE_POS_CRNT_TOTAL_ENERGY,FM_BEG,&ETot);
     //FileMan(FM_WRITE,FILE_ENERGY,FM_DP,1,
     //   FILE_POS_CRNT_TOTAL_ENERGY,FM_BEG,&Ediel);
     QFree(jHv_cosmo);
     */
  }

    // ZQY: Save MOs for DC and DCRelax calc.
    int saveSub = rem_read(REM_SAVE_SUBSYSTEM);
    if ( saveSub==10 || saveSub==20
	|| saveSub==11 || saveSub==21 ) {
      int SUB_MO_COEFS;
      switch (saveSub) {
      case 10:
          SUB_MO_COEFS = SUB_MO_COEFS_10;
          break;
      case 20:
          SUB_MO_COEFS = SUB_MO_COEFS_20;
          break;
      case 11:
          SUB_MO_COEFS = SUB_MO_COEFS_11;
          break;
      case 21:
          SUB_MO_COEFS = SUB_MO_COEFS_21;
          break;
      default:
          QCrash("invalid value for SAVE_SUBSYSTEM");
      }
      FileMan(FM_WRITE,SUB_MO_COEFS,FM_DP,N*NOrb,0,FM_BEG,jCA);
      FileMan(FM_WRITE,SUB_MO_COEFS,FM_DP,N*NOrb,0,FM_CUR,jCB);
      FileMan(FM_WRITE,SUB_MO_COEFS,FM_DP,NOrb,  0,FM_CUR,jEA);
      FileMan(FM_WRITE,SUB_MO_COEFS,FM_DP,NOrb,  0,FM_CUR,jEB);
    }

    GUIDumpData(GUI_DATA_SCF_ENERGY,ETot);

    // While we have the Fock matrices loaded up...
//NVO
    if (usingGDM || usingDM || usingGDIIS) {
      /* make canonical (or pseudocanonical) orbitals & get eigenvalues
	 for gradient, CIS, etc... Note we must skip this for ROHF */
      if (jCA == NULL) jCA = QAllocDouble(N*NOrb*NMO);
//NVO
      if (jEA == NULL) jEA = QAllocDouble(NOrb*NMO);
      double* jU   = QAllocDouble(N2); /* !!! Reuse existing matrices? */
      double* jFvo = QAllocDouble(N2);
      double* jS1  = QAllocDouble(N2);
      if (ISCF != 2) {
	i = NOrb - NAlpha;
	if (i > 0)
	  pseuco(jU,jEA,jFvo,jCA,jFA,jS1,&N,&NOrb,&NAlpha,&i,&True);
	else
	  pseuco(jU,jEA,jFvo,jCA,jFA,jS1,&N,&NOrb,&NAlpha,&i,&False);
	if (NMO == 2) {
	  i = NOrb - NBeta;
	  if (NBeta > 0 && i > 0)
	    pseuco(jU,jEB,jFvo,jCB,jFB,jS1,&N,&NOrb,&NBeta,&i,&True);
	  else
	    pseuco(jU,jEB,jFvo,jCB,jFB,jS1,&N,&NOrb,&NBeta,&i,&False);
	}
      }
      else {
        double* jS3 = QAllocDouble(N2);
        double* jS4 = QAllocDouble(N2);

	// Added so GDIIS is OK
	if(usingGDIIS){
	  if (NOA != NOB || JustAl != 0) ISCF = 1;
	  NTheta = NOA*NVA + ISCF*NOB*NVB;
	  if (ISCF == 1 && JustAl == 0) {
	    ISCF = 2;
	    NTheta = NOB*NVA + (NOA-NOB)*(NVA+NOB);
	  }}

        ropseu(jU,jEA,&EMax,jFA,jFB,jCA,jS1,jFvo,jS3,jS4,&NAlpha,&NBeta,
               &NOrb,&NTheta,&N,&True);
	QFree(jS4);
	QFree(jS3);
	moengy(jEA,jCA,jFA,jS1,jFvo,&N,&NOrb);
	moengy(jEB,jCA,jFB,jS1,jFvo,&N,&NOrb);
      }
      QFree(jU);
      QFree(jFvo);
      QFree(jS1);
      //AML
      if (!NoSCF){
	FileMan(FM_WRITE,FILE_MO_COEFS,FM_DP,N*NOrb,0,FM_BEG,jCA);
	FileMan(FM_WRITE,FILE_MO_COEFS,FM_DP,N*NOrb,0,FM_CUR,jCB);
	FileMan(FM_WRITE,FILE_MO_COEFS,FM_DP,NOrb,  0,FM_CUR,jEA);
	FileMan(FM_WRITE,FILE_MO_COEFS,FM_DP,NOrb,  0,FM_CUR,jEB);
      }
    }

    // Orient the MOs once and for all for consistent use with
    // the post-HF symmetry code
    // unless we are working with ALMOs
    if (NoSCF) printf("COACH_MP2: preserving saved MOs; skipping post-SCF orientation\n");
    if (!NoSCF && !(LPSCFMI > 0 && LPCorr==0) && rem_read(REM_SMX_SOLVATION) != -1)
      orimo(qalloc_start(),(INTEGER*)qalloc_start());

    INTEGER NCC = rem_read(REM_CORE_CHARACTER);
    if (NCC>0){
      //    VAR 05/01  Permute occupied orbitals according to core character
      Core_char(NCC);
    }
    // Reorder MOs here, unless we are running a ccman job, in which case
    // we let ccman do it.
    if (rem_read(REM_REORDERMOS) && rem_read(REM_LEVCOR) < 200) {

    	int whatrem = rem_read(REM_REORDERMOS);

	int i, j, nvalence, ncore, nvirt = 0;

	ncore = rem_read(REM_CC_REST_OCC);
	nvirt = rem_read(REM_CC_REST_VIR);
	nvalence = NOrb - ncore - nvirt;

	int* Swap = QAllocINTEGER(whatrem/2);

	double* jCoef = QAllocDouble(NBasis*NOrb);
	double* jEVal = QAllocDouble(NOrb);
	double* jCbak = QAllocDouble(NBasis*NOrb);
	double* jEbak = QAllocDouble(NOrb);
	int* Indx = QAllocINTEGER(NOrb);
	// i loops for alpha and beta mos and eigenvalues
	FileMan_Open_Read(FILE_REORDER_MO);

	for(i = 0; i < 2; i++)
	  {
	    FileMan(FM_READ,FILE_MO_COEFS,FM_DP,NBasis*NOrb,i*NBasis*NOrb,FM_BEG,jCbak);
	    FileMan(FM_READ,FILE_MO_COEFS,FM_DP,NOrb,NBasis*NOrb*2+i*NOrb,FM_BEG,jEbak);
	    // read in desired order of valence mos
	    FileMan(FM_READ,FILE_REORDER_MO,FM_INT,whatrem/2,0,
		    (i==0)?FM_BEG:FM_CUR,Swap);

	    swaporbitals(jCoef,jEVal,jCbak,jEbak,&NBasis,Swap,&NOrb,Indx);
	    FileMan(FM_WRITE,FILE_MO_COEFS,FM_DP,NBasis*NOrb,i*NBasis*NOrb,FM_BEG,jCoef);
	    FileMan(FM_WRITE,FILE_MO_COEFS,FM_DP,NOrb,NBasis*NOrb*2+i*NOrb,FM_BEG,jEVal);

	    if (i == 0)
	      cout << "\n   ***Reordering MOs*** \n\n Alpha Reordered MOs:\n";
	    else
	      cout << "\n Beta Reordered MOs:\n";

	    for(j = 0; j < (whatrem/2); j++)
	      {
		cout << " " << Swap[j] ;
	      }
	    cout << "\n";
	  }
	FileMan_Close(FILE_REORDER_MO);
	QFree(Swap);
	QFree(jCoef);
	QFree(jEVal);
	QFree(jEbak);
	QFree(jCbak);
	QFree(Indx);
      }
  {
      DevKeyword devREM;
      if(devREM.getValue("scf_corresponding_orbs")){
          //
          printf(" Obtaining Corresponding orbitals\n");
          get_corresponding_orbs();
      };
  };

  }
  else {
    SCFfinalPrint(jEA, jEB, jCA, jCB, jFA, jFB, N,
		  NAlpha, NBeta, NMO, (usingGDM || usingDM));
    if (!MP2Restart && GuessImpr == 0) { // original code was !GuessImpr>0){
       if (rem_read(REM_SMALL_BASIS_LARGE_BASIS) != 1 || rem_read(REM_DUAL_BASIS_ENERGY) != 1)
         QCrash("SCF failed to converge");
    }
    printf(" SCF time:  CPU %.2f s  wall %.2f s\n",t1[0],t1[2]);
  }

  // IMOM - Update the guess orbitals in case there is a follow on job
  if (rem_read(REM_MOM_START) > 0 && !NoSCF) {
     FileMan(FM_WRITE, FILE_GUESS_MO_COEFS, FM_DP, NBasis*NOrb, 0, 1, jCA);
     FileMan(FM_WRITE, FILE_GUESS_MO_COEFS, FM_DP, NBasis*NOrb, 0, 2, jCB);
     FileMan(FM_WRITE, FILE_GUESS_MO_COEFS, FM_DP, NOrb,        0, 2, jEA);
     FileMan(FM_WRITE, FILE_GUESS_MO_COEFS, FM_DP, NOrb,        0, 2, jEB);
  }

  if (dc_dft)
     printf(" SCF final print not available for DC-DFT\n");
  else
     SCFfinalPrint(jEA, jEB, jCA, jCB, jFA, jFB, N, NAlpha, NBeta, NMO, (usingGDM || usingDM));

  // Save orbitals and density to archive
  libarchive::qchem::qarchscf_save_results(NBasis, NOrb, Unrestricted);

/*
  if (fractional_occupations > 0) {
    // Fractional SCF occupations (DSL)
    printf("*** Extrapolation to Zero Kelvin ***\n");
    // Extrapolate density to Zero Kelvin

    double Tzero = 0.0;
    const int NAct = rem_read(REM_FON_NORB); // number of active orbitals
    double* jPA = QAllocDouble(N2*NDen);
    double* jPB = jPA + N2;

    MO2DenFrac(jPA,jCA,jEA,N,0,NAlpha,false,Tzero,NAlpha,NAct,EMax);
    if (NDen == 2) {
      MO2DenFrac(jPB,jCB,jEB,N,0,NBeta,false,Tzero,NBeta,NAct,EMax);
    }

    // Get zero-Kelvin energy

    double ESCF = 0.0;
    double* PF = QAllocDoubleWithInit(N2*NDen);

    AtimsB(PF, jPA, jFA, N, N, N, N, N, N, 1);
    VRtrace(&ESCF, PF, N2);

    printf("E_SCF(0K) = %20.10f\n", ESCF);

    QFree(PF);
    QFree(jPA);
  }
*/

  if(trans_enable == 1){
    if(tran_opt<=3) {
      int Analysis=1;
      transcpp_main(NBasis,NOrb,NMO,NDen,jFA,jFB,jPA,jPB,jS,IteSCF,2,Analysis);
    }
    if(usingNEGF) trans_NEGF_cleanup_files();
  } else
  if(trans_enable == -1){
    int Analysis=-1; // only printing of dat files!
    transcpp_main(NBasis,NOrb,NMO,NDen,jFA,jFB,jPA,jPB,jS,IteSCF,2,Analysis);
  }


  if (rem_read(REM_DUAL_BASIS_ENERGY) == 1 && rem_read(REM_SMALL_BASIS_LARGE_BASIS) != 1) {
     // small basis calculation converged
     // save C, P, CC^t to disk
     save_cct(NBasis, NOrb, NMO, jCA, jEA, jFA);
  }
  else if (rem_read(REM_DUAL_BASIS_ENERGY) == 1 && rem_read(REM_SMALL_BASIS_LARGE_BASIS) == 1) {
     // large basis
     FileMan(FM_READ,FILE_DENSITY_MATRIX,FM_DP,NBasis*NBasis*NMO,0,FM_BEG,jPA);
     FileMan(FM_WRITE,FILE_BIG_BASIS_DENSITY_BIGBAS,FM_DP,NBasis*NBasis*NMO,0,FM_BEG,jPA);
     if ( XCFunc.IsPureDFT() && !(add_LRK || LRC) && ((!dc_dft && !dscf_eda) || (dc_dft && have_hfdens) || 
         (dscf_eda && have_hfdens)) ) QFree(jPA);
  }

  if (rem_read(REM_HFPT_BASIS) > 0 && rem_read(REM_DOMP2V) < 0) HFPTman();

   if( rem_read(REM_ARI) )
     {
       void clearARIJK(void);
       clearARIJK();
     }

  if(do_mrXC) {
    delete interp_grid;
    desetXCSmoothS2();
  }

  //AIK, to fix crashes with SCF restarts
  if (rem_read(REM_DUAL_BASIS_ENERGY)==1 || MaxSCF !=1)
  {
      QFree(jCA);
      QFree(jEA);
      QFree(jFA);
  }
  if (rem_read(REM_ROKS)>0)
      QFree(jC0);

  if ((XCFunc.HasHF() || add_LRK || LRC || mf.iSaveMinima) || (dc_dft && XCFunc.IsPureDFT()) || 
      (dscf_eda && XCFunc.IsPureDFT()))
  {
     QFree(jPA);
     //EJS MemLeakFix
     if (XCFunc.HasHF() && LRC)
     {
        QFree(jKAsr);
     }
  }
  if(jxRCA != NULL){
    QFree(jxRCA);
    QFree(jARCA);
    QFree(jERCA);
    QFree(jE0RCA);
    QFree(jdxRCA);
    QFree(jgxRCA);
  }
  QFree(jFAv);
  QFree(jPAv);
  QFree(jXCAv);
  if (dc_dft || dscf_eda) QFree(jJv_temp);
  if (canUseGDM || canUseDM) qfree(jTh);
  if (rem_read(REM_DOMOS_DFT) > 0 || XCFunc.HasTau()) QFree(jCAXC);
  resetSymmetry();
  QFree(jS);

  //cout << "before print summary" << endl;

  if (do_efp) {
      EFP2::instance().compute_integral_pairwise_energy(ETot, 0);
      EFP2::instance().print_energy();
  }

  if (MP2Restart){
      // ETot = Hartree-Fock functional evaluated with the saved MOs
      FileMan(FM_WRITE,FILE_ENERGY,FM_DP,1,FILE_POS_CRNT_TOTAL_ENERGY,FM_BEG,&ETot);
      FileMan(FM_WRITE,FILE_ENERGY,FM_DP,1,FILE_POS_SCF_ENERGY,FM_BEG,&ETot);
  }

/*
  // Replace normal MOs with COVPs to print them out later
  if (rem_read(REM_EDA_PRINT_COVP)>0 && rem_read(REM_EDA_COVP)>0) {
//     INTEGER DPtoMove=2*NOrb*N+2*NOrb;
//     double* tempR=QAllocDouble(DPtoMove);
//     FileMan(FM_READ,FILE_MO_COVP,FM_DP,DPtoMove,0,FM_BEG,tempR);
//     FileMan(FM_WRITE,FILE_MO_COEFS,FM_DP,DPtoMove,0,FM_BEG,tempR);
//     QFree(tempR);

      String QCFilePref;
      if (!(QCFilePref = getenv("QCFILEPREF")))
        QCrash("Cannot read QCFILEPREF environment variable");
      InFile = QCFilePref + FILE_MO_COVP + ".0";
      String OutputFile = QCFilePref + FILE_MO_COEFS + ".0";
      FileCopy(InFile, OutputFile);

  }
*/

#ifdef RUSTY
  //RST: time scf
  QTimerOff(rusty01,rusty00);
  printf("TIMEINFO->: entire scfman.C %.2f sec.\n",rusty01[0]);
#endif

   // smx solvation
   if (rem_read(REM_SMX_SOLVATION) >= 1) 
   {
      FileMan(FM_WRITE,FILE_SOLVATION_ENERGY_COMPONENTS,FM_DP,1,3,FM_BEG,&ETot);
      smx_final_print();
   }
   else if (rem_read(REM_SMD_PCM) == 1) 
   {
      double Zero = 0.0;
      FileMan(FM_WRITE,FILE_SOLVATION_ENERGY_COMPONENTS,FM_DP,1,2,FM_BEG,&Zero);
      FileMan(FM_WRITE,FILE_SOLVATION_ENERGY_COMPONENTS,FM_DP,1,3,FM_BEG,&ETot);
      smd_final_print();
   }

   rem_write(IteSCF,REM_SCF_CYCLES);

   if(jQj != NULL) QFree(jQj);
   qfree(jTop);
}

// Read a density guess from somewhere (disk, usually) and populate either
// the vectorized or dense density matrices.
// People using fancy methods that need to be clever about what guess density
// to use should hook in here.  It is probably best to use global state for
// checking this (e.g. a rem variable enabling the method), but it would not
// be the end of the world if extra parameters were added to this routine.
// use_Pv	-- true if using vectorized matrices
// NDen		-- whether one or two density matrices are in use
// jP{A,B}{v,}	-- output density matric(es)
// -BJK, 29 Feb 2012
static void
scfman_read_guess_density(bool use_Pv, INTEGER NDen, double *jPAv, double *jPBv,
    double *jPA, double *jPB)
{
    INTEGER NBasis = bSetMgr.crntShlsStats(STAT_NBASIS);
    INTEGER NB2    = rem_read(REM_NB2);

    if (rem_read(REM_CDFTCI) != 0) {
	// CDFT-CI involves multiple SCF calculations on distinct states;
	// as such the logic needs to be more complicated.
	cdftci_read_guess_density(use_Pv, NDen, jPAv, jPBv, jPA, jPB,
	    NBasis, NB2);
    } else if (use_Pv) {
	// default case; no one has any better ideas for what to do than to
	// take what GuessMan has put on disk in the usual spot.
	if (use_Pv) {
	    // Can use sparse form of P
	    FileMan_Open_Read(FILE_SPARSE_DENSITY_MATRIX);
	    FileMan(FM_READ,FILE_SPARSE_DENSITY_MATRIX,FM_DP,NB2,0,FM_BEG,jPAv);
	    if (NDen == 2)
		FileMan(FM_READ,FILE_SPARSE_DENSITY_MATRIX,FM_DP,NB2,0,FM_CUR,jPBv);
	    FileMan_Close(FILE_SPARSE_DENSITY_MATRIX);
	}
    } else {
	// Use dense form of P
	if(rem_read(REM_TRIPLET) == 1){
	    FileMan(FM_READ,FILE_DENS_T_MATRIX,FM_DP,NBasis*NBasis,0,FM_BEG,jPA);
	    if (NDen == 2)
		FileMan(FM_READ,FILE_DENS_T_MATRIX,FM_DP,NBasis*NBasis,0,FM_CUR,jPB);
	}else{
	    FileMan(FM_READ,FILE_DENSITY_MATRIX,FM_DP,NBasis*NBasis,0,FM_BEG,jPA);
	    if (NDen == 2)
		FileMan(FM_READ,FILE_DENSITY_MATRIX,FM_DP,NBasis*NBasis,0,FM_CUR,jPB);
	}

	if (rem_read(REM_CDFTCI_FRAGMENT)>0) {
	    FileMan_Open_Read(FILE_CDFTCI_DENSITY_GUESS);
	    FileMan(FM_READ,FILE_CDFTCI_DENSITY_GUESS,FM_DP,NBasis*NBasis,0,FM_BEG,jPA);
	    if (NDen == 2)
               FileMan(FM_READ,FILE_CDFTCI_DENSITY_GUESS,FM_DP,NBasis*NBasis,0,FM_BEG,jPB);
	    FileMan_Close(FILE_CDFTCI_DENSITY_GUESS);
	}
    }
}

////////////////////////////////////////////////////////

void AddFractionalElectron(double *jPA, double *jCA)
{
  double f = 0.001*(double)rem_read(REM_FRACTIONAL_ELECTRON);
  if (f > 0.0)
     printf("Adding %.3f of an alpha electron to the LUMO\n",f);
  else if (f < 0.0)
     printf("Subtracting %.3f of an alpha electron from the HOMO\n",-f);
  INTEGER NBasis = bSetMgr.crntShlsStats(STAT_NBASIS);
  INTEGER NAlpha = rem_read(REM_NALPHA);
  INTEGER n = (f > 0.0) ? NAlpha+1 : NAlpha; // LUMO or HOMO
  add_frac_elec(jPA,jCA,&n,&NBasis,&f);
}

#undef JMHDEBUG
