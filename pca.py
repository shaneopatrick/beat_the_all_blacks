import h2o
import pandas
from h2o.estimators.pca import H2OPrincipalComponentAnalysisEstimator as H2OPCA

if __name__ == '__main__':

    df = h2o.import_file("complete_df.csv")

    cols = df.columns

    # Train with the Power pca_method
    pca = H2OPCA(k = 1, transform = "STANDARDIZE", pca_method="Power",
                       use_all_factor_levels=True, impute_missing=True)
    pca.train(x=cols[1:], training_frame=df)

    # View the importance of components
    print(pca.varimp(use_pandas=False))

    # # View the eigenvectors
    eg = pca.rotation().as_data_frame()
    print(eg.sort_values('pc1', ascending=False))


# # Train again with the GLRM pca_method
# birds2 = h2o.import_file("https://s3.amazonaws.com/h2o-public-test-data/smalldata/pca_test/birds.csv")
# birds2.pca = H2OPrincipalComponentAnalysisEstimator(k = 3, transform = "STANDARDIZE",
#                     pca_method="GLRM", use_all_factor_levels=True,
#                     impute_missing=True)
# birds2.pca.train(x=list(range(4)), training_frame=birds2)
#
# # View the importance of components
# birds2.pca.varimp(use_pandas=False)
# [(u'Standard deviation', 1.9286830840160667, 0.2896650415698226, 0.2053712844270903),
# (u'Proportion of Variance', 0.9672162180423401, 0.021816948059531167, 0.01096683389812861),
# (u'Cumulative Proportion', 0.9672162180423401, 0.9890331661018713, 0.9999999999999999)]
#
# # View the eigenvectors
# birds2.pca.rotation()
# Rotation:
#                    pc1                pc2                pc3
# -----------------  -----------------  -----------------  -----------------
# patch.Ref1a        -0.0973454860413    0.0233748845619   -0.0407839669099
# patch.Ref1b        -0.0979880717715    -0.0167446302072  -0.0162149496631
# patch.Ref1c        -0.0971529563124    0.00536661170128  -0.0177009628488
# patch.Ref1d        -0.100657197505     0.00754923938494  -0.018364320893
# patch.Ref1e        -0.0982933822825    0.0158116058361   -0.0193764027317
# ---                ---                 ---               ---
# landscape.Bauxite  -0.0248166745792    -0.504864083913   0.074374750806
# landscape.Forest   -0.0296555294277    0.232678445269    -0.537738667852
# landscape.Urban    -0.0733909967344    -0.112998988851   0.0347355699687
# S                  0.00878461186804    0.649068763107    -0.130282514102
# year               -0.000583301909773  -0.0765116904321  -0.69416666169
#
# See the whole table with table.as_data_frame()
