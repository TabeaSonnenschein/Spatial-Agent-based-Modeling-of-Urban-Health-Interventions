library("r2pmml")

variable_subset = "allvars"
variable_subset = "allvars_strict"

PCstat = "NOPCA"
PCstat = "PCA"

if(PCstat == "NOPCA"){
    setwd("D:/PhD EXPANSE/Data/CBS microdata/230426_0500_9234_DecisionTree_VarSubsetTesting/9234_DecisionTree_VarSubsetTesting/07 DecisionTreesAndImportanceMetrics/NoPCA")
    load(paste0(variable_subset,"_DecisionTreeModel", PCstat,".RData"))
    VarOrder = read.table(paste0(variable_subset,"_order_predvars", PCstat, ".txt"))
} else{
    setwd("D:/PhD EXPANSE/Data/CBS microdata/230426_0500_9234_DecisionTree_VarSubsetTesting/9234_DecisionTree_VarSubsetTesting/07 DecisionTreesAndImportanceMetrics/WithPCA")
    load(paste0(variable_subset,"_DecisionTreeModel.RData"))
    VarOrder = read.table(paste0(variable_subset,"_order_predvars.txt"))
}

setwd("C:/Users/Tabea/Documents/PhD EXPANSE/Data/Amsterdam/ModalChoiceModel")
r2pmml(model, paste0("modalChoice_", variable_subset, PCstat,".pmml"))
write.csv(VarOrder, paste0("OrderPredVars_", variable_subset, PCstat, ".csv"), row.names = F)
