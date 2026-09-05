#!/bin/bash
#SBATCH --job-name=rev_q2_qchem_build
#SBATCH --partition=cm1
#SBATCH --account=lr_qchem
#SBATCH --qos=condo_qchem
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=16
#SBATCH --mem=128G
#SBATCH --time=12:00:00
#SBATCH --output=/clusterfs/mhg-data/yaoshen/coach-based_dh_data/revwb97m2/qchem_builds/logs/q2_qchem_build_%j.out
#SBATCH --error=/clusterfs/mhg-data/yaoshen/coach-based_dh_data/revwb97m2/qchem_builds/logs/q2_qchem_build_%j.err

set -euo pipefail

source_root=/clusterfs/mhg-data/yaoshen/qchem/trunk
libks_root=/clusterfs/mhg-data/yaoshen/qchem/trunk/libks
install_root=/clusterfs/mhg-data/yaoshen/coach-based_dh_data/revwb97m2/qchem_builds/qchem-r48798-libks-r1666-idv-8d40ca02
compiler_root=/global/software/rocky-8.x86_64/gcc/linux-rocky8-x86_64/gcc-8.5.0/gcc-10.5.0-obvhoavhjnrlqxypkfzr53nbrlywiuws
expected_qchem_revision=48798
expected_libks_revision=1666
expected_diff_sha256=8d40ca02fac8edd3f1d99886755a0a7794c462bbcb606f2378f23eabb5570bf0

export PATH="${compiler_root}/bin:${PATH}"
export CC="${compiler_root}/bin/gcc"
export CXX="${compiler_root}/bin/g++"
export FC="${compiler_root}/bin/gfortran"

mkdir -p "${install_root}"
if [[ -e "${install_root}/BUILD_COMPLETE" ]]; then
    echo "Refusing to overwrite completed build ${install_root}" >&2
    exit 2
fi
if [[ -e "${install_root}/build/CMakeCache.txt" ]]; then
    echo "Refusing to reuse a previously configured incomplete build tree." >&2
    exit 2
fi

actual_qchem_revision=$(svn info --show-item revision "${source_root}")
actual_libks_revision=$(svn info --show-item revision "${libks_root}")
actual_diff_sha256=$(svn diff "${libks_root}" | sha256sum | awk '{print $1}')
if [[ "${actual_qchem_revision}" != "${expected_qchem_revision}" ]]; then
    echo "Q-Chem revision changed: ${actual_qchem_revision}" >&2
    exit 3
fi
if [[ "${actual_libks_revision}" != "${expected_libks_revision}" ]]; then
    echo "libks revision changed: ${actual_libks_revision}" >&2
    exit 3
fi
if [[ "${actual_diff_sha256}" != "${expected_diff_sha256}" ]]; then
    echo "libks diff changed: ${actual_diff_sha256}" >&2
    exit 3
fi

test "$(sha256sum "${libks_root}/libks/CMakeLists.txt" | awk '{print $1}')" = afa25d4a7d744b84ac395fbf599cb1ff4ce2161cbd863c03218206128e0b04db
test "$(sha256sum "${libks_root}/libks/drivers/ks_driver_exc.C" | awk '{print $1}')" = 35d752de612ea206a6e4d72f2ef7ed6fc7aac8535e5ead4da9c12a5af2b36d22
test "$(sha256sum "${libks_root}/libks/exc_fxc/integrated_dv.C" | awk '{print $1}')" = 7c1ce184380c2b79f96c9b8b3fe99823f4b23ae43a1ca6277d92697f99ef1199
test "$(sha256sum "${libks_root}/libks/exc_fxc/integrated_dv.h" | awk '{print $1}')" = 193ec198bd088bfca9cea13cf300537f426b84198043ca889aed94236ab4912c

{
    echo "started_utc=$(date -u +%Y-%m-%dT%H:%M:%SZ)"
    echo "slurm_job_id=${SLURM_JOB_ID:-not_slurm}"
    echo "hostname=$(hostname -f)"
    echo "qchem_svn_url=$(svn info --show-item url "${source_root}")"
    echo "qchem_svn_revision=${actual_qchem_revision}"
    echo "libks_svn_url=$(svn info --show-item url "${libks_root}")"
    echo "libks_svn_revision=${actual_libks_revision}"
    echo "libks_local_diff_sha256=${actual_diff_sha256}"
    echo "cmake=$(cmake --version | head -n 1)"
    echo "make=$(make --version | head -n 1)"
    echo "cc=$(${CC} --version | head -n 1)"
    echo "cxx=$(${CXX} --version | head -n 1)"
    echo "fc=$(${FC} --version | head -n 1)"
    echo "configure_arguments=gnu openmp relwdeb version"
} > "${install_root}/build_provenance.txt"

cd "${install_root}"
QCBUILD=build "${source_root}/configure" gnu openmp relwdeb version
cmake --build build --parallel "${SLURM_CPUS_PER_TASK}" 2>&1 | tee build.log
cmake --install build 2>&1 | tee install.log

executable="${install_root}/exe/qcprog.exe"
test -s "${executable}"
sha256sum "${executable}" > "${install_root}/executable.sha256"
ldd "${executable}" > "${install_root}/executable.ldd.txt"
if rg -n 'not found' "${install_root}/executable.ldd.txt"; then
    echo "Unresolved executable dependency." >&2
    exit 4
fi
{
    echo "completed_utc=$(date -u +%Y-%m-%dT%H:%M:%SZ)"
    echo "executable=$(realpath "${executable}")"
    echo "executable_sha256=$(sha256sum "${executable}" | awk '{print $1}')"
    echo "executable_bytes=$(stat -c %s "${executable}")"
} >> "${install_root}/build_provenance.txt"
touch "${install_root}/BUILD_COMPLETE"
