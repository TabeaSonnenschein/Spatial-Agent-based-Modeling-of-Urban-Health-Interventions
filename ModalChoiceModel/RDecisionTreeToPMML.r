library("r2pmml")

# variable_subset = "allvars"
variable_subset = "allvars_strict"


setwd("D:/PhD EXPANSE/Data/CBS microdata/230426_0500_9234_DecisionTree_VarSubsetTesting/9234_DecisionTree_VarSubsetTesting/07 DecisionTreesAndImportanceMetrics/NoPCA")
load(paste0(variable_subset,"_DecisionTreeModelNOPCA.RData"))
VarOrder = read.table(paste0(variable_subset,"_order_predvarsNOPCA.txt"))

setwd("C:/Users/Tabea/Documents/PhD EXPANSE/Data/Amsterdam/ModalChoiceModel")
r2pmml(model, "modalChoice.pmml")
write.csv(VarOrder, "OrderPredVars.csv", row.names = F)
