#ifndef LIBKS_INTEGRATED_DV_H
#define LIBKS_INTEGRATED_DV_H

#include <armadillo>
#include <cstddef>

namespace libks
{

constexpr size_t integrated_dv_rows = 96;
constexpr size_t integrated_dv_cols = 180;

/** Accumulate the COACH integrated-density-variable feature matrix for one grid batch. */
void eval_integrated_dv(const size_t ngrid,
    const arma::vec &grid_weights,
    const arma::vec &Rhoa, const arma::vec &Rhob,
    const arma::mat &Rhoa1, const arma::mat &Rhob1,
    const arma::vec &Taua, const arma::vec &Taub,
    arma::mat &integrated_dv_batch);

}  // namespace libks

#endif  // LIBKS_INTEGRATED_DV_H
