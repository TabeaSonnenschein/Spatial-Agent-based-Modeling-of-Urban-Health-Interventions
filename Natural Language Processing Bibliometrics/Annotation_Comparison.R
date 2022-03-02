install.packages("psych")
library(psych)

setwd("C:/Users/Tabea/Documents/PhD EXPANSE/Literature/WOS_ModalChoice_Ref/CrossrefResults/manually_labeled")
annots = read.csv("AnnotationValidation_article1_comparison.csv")

which(annots$Word == "Discussion")
Results_section = annots[2183:3270, ]
cohen.kappa(annots[, c("Tabea_Tag", "Simon_Tag")])


nr_diff_tot = length(which(annots$Tabea_Tag != annots$Simon_Tag))
perc_overlap = (length(annots$Tabea_Tag)-nr_diff_tot)/length(annots$Tabea_Tag)
Non_overlap_subset = annots[which(annots$Tabea_Tag != annots$Simon_Tag),]

nr_diff_tot_results = length(which(Results_section$Tabea_Tag != Results_section$Simon_Tag))
perc_overlap_results = (length(Results_section$Tabea_Tag)-nr_diff_tot_results)/length(Results_section$Tabea_Tag)
Non_overlap_subset_results = Results_section[which(Results_section$Tabea_Tag != Results_section$Simon_Tag),]
cohen.kappa(Results_section[, c("Tabea_Tag", "Simon_Tag")])
# Union of intersection
# Behavior Options
Nr_BO_Tabea = length(which(annots$Tabea_Tag == "I-behavOption"))
Nr_BO_Simon = length(which(annots$Simon_Tag == "I-behavOption"))
perc_diff_BO = (Nr_BO_Simon - Nr_BO_Tabea) / Nr_BO_Tabea

# Association Types
Nr_AT_Tabea = length(which(annots$Tabea_Tag == "I-assocType"))
Nr_AT_Simon = length(which(annots$Simon_Tag == "I-assocType"))
perc_diff_AT = (Nr_AT_Simon - Nr_AT_Tabea) / Nr_AT_Tabea

# Behavior Determinants
Nr_BD_Tabea = length(which(annots$Tabea_Tag == "I-behavDeterm"))
Nr_BD_Simon = length(which(annots$Simon_Tag == "I-behavDeterm"))
perc_diff_BD = (Nr_BD_Simon - Nr_BD_Tabea) / Nr_BD_Tabea

# Study Groups
Nr_SG_Tabea = length(which(annots$Tabea_Tag == "I-studygroup"))
Nr_SG_Simon = length(which(annots$Simon_Tag == "I-studygroup"))
perc_diff_SG = (Nr_SG_Simon - Nr_SG_Tabea) / Nr_SG_Tabea

unique(annots$Tabea_Tag)
unique(annots$Simon_Tag)
