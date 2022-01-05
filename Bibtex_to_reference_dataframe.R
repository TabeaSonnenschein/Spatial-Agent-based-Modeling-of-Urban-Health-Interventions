pkgs = c("stringr", "mgsub")
# sapply(pkgs, install.packages, character.only = T) #install packages if necessary
sapply(pkgs, require, character.only = T) #load 

setwd("C:/Users/Tabea/Documents/PhD EXPANSE/Written Paper/02- Behavioural Model paper")
ref_data = read.csv("search5_reference_data.csv")

length(which(!is.na(str_extract(ref_data$ï..input, "^file*"))))

ref_data_clean = as.data.frame(matrix(nrow = 214, ncol = 14))
colnames(ref_data_clean)= c("article_id", "doc_type", "title", "abstract", "author", "doi", "file", "issn", "journal", "keywords", "number", "pages", "volume", "year")
endings = which(!is.na(str_extract(ref_data$ï..input, "^\\}")))

ref_data_clean$article_id = ref_data$ï..input[c(1,(endings[1:(length(endings)-1)] +1))]
ref_data_clean$doc_type[which(!is.na(str_extract(ref_data_clean$article_id, "@article*")))] = "article"
ref_data_clean$doc_type[which(!is.na(str_extract(ref_data_clean$article_id, "@book*")))] = "book"
ref_data_clean$article_id = mgsub(ref_data_clean$article_id, c("@article\\{", ",", "@book\\{"), c("", "", ""))

for(paper in 1:nrow(ref_data_clean)){
  current_p = c(1,endings)[paper]
  next_p = c(1,endings)[paper+1]
  paper_info = ref_data$ï..input[current_p:next_p]
  ref_data_clean$file[paper] = paper_info[which(!is.na(str_extract(paper_info, "^file*")))] 
  ref_data_clean$title[paper] =  paper_info[which(!is.na(str_extract(paper_info, "^title*")))]
  if(TRUE %in% !is.na(str_extract(paper_info, "^abstract*"))){
    ref_data_clean$abstract[paper] =  paper_info[which(!is.na(str_extract(paper_info, "^abstract*")))]
  }
  if(TRUE %in% !is.na(str_extract(paper_info, "^journal*"))){
    ref_data_clean$journal[paper] =  paper_info[which(!is.na(str_extract(paper_info, "^journal*")))]
  }
  if(TRUE %in% !is.na(str_extract(paper_info, "^keywords*"))){
    ref_data_clean$keywords[paper] =  paper_info[which(!is.na(str_extract(paper_info,  "^keywords*")))]
  }    
  if(TRUE %in% !is.na(str_extract(paper_info, "^doi*"))){
    ref_data_clean$doi[paper] =  paper_info[which(!is.na(str_extract(paper_info, "^doi*")))]
  }
  if(TRUE %in% !is.na(str_extract(paper_info, "^author*"))){
    ref_data_clean$author[paper] =  paper_info[which(!is.na(str_extract(paper_info, "^author*")))]
  }
  if(TRUE %in% !is.na(str_extract(paper_info, "^issn*"))){
    ref_data_clean$issn[paper] =  paper_info[which(!is.na(str_extract(paper_info,  "^issn*")))]
  } 
  if(TRUE %in% !is.na(str_extract(paper_info, "^number*"))){
    ref_data_clean$number[paper] =  paper_info[which(!is.na(str_extract(paper_info, "^number*")))]
  }
  if(TRUE %in% !is.na(str_extract(paper_info, "^pages*"))){
    ref_data_clean$pages[paper] =  paper_info[which(!is.na(str_extract(paper_info, "^pages*")))]
  }
  if(TRUE %in% !is.na(str_extract(paper_info, "^volume*"))){
    ref_data_clean$volume[paper] =  paper_info[which(!is.na(str_extract(paper_info,  "^volume*")))]
  } 
  if(TRUE %in% !is.na(str_extract(paper_info, "^year*"))){
    ref_data_clean$year[paper] =  paper_info[which(!is.na(str_extract(paper_info,  "^year*")))]
  }
}

ref_data_clean$title =  mgsub(ref_data_clean$title, c("title = \\{\\{", "\\}\\},"), c("", ""))
ref_data_clean$abstract = mgsub(ref_data_clean$abstract, c("abstract = \\{", "\\},"), c("", ""))
ref_data_clean$file = mgsub(ref_data_clean$file, c("file = \\{:", ":pdf\\},"), c("", ""))
ref_data_clean$file_name = mgsub(ref_data_clean$file, c("C.:/Users/Tabea/Documents/PhD EXPANSE/Literature/WOS_ModalChoice_Ref/search2/", "C.:/Users/Tabea/Documents/PhD EXPANSE/Literature/WOS_ModalChoice_Ref/search3/"), c("", ""))
ref_data_clean$author =  mgsub(ref_data_clean$author, c("author = \\{", "\\},"), c("", ""))
ref_data_clean$doi = mgsub(ref_data_clean$doi, c("doi = \\{", "\\},"), c("", ""))
ref_data_clean$issn = mgsub(ref_data_clean$issn, c("issn = \\{", "\\},"), c("", ""))
ref_data_clean$journal = mgsub(ref_data_clean$journal, c("journal = \\{", "\\},"), c("", ""))
ref_data_clean$volume = mgsub(ref_data_clean$volume, c("volume = \\{", "\\},"), c("", ""))
ref_data_clean$number = mgsub(ref_data_clean$number, c("number = \\{", "\\},"), c("", ""))
ref_data_clean$keywords = mgsub(ref_data_clean$keywords, c("keywords = \\{", "\\},"), c("", ""))
ref_data_clean$year = mgsub(ref_data_clean$year, c("year = \\{", "\\}"), c("", ""))
ref_data_clean$pages = mgsub(ref_data_clean$pages, c("pages = \\{", "\\},"), c("", ""))

write.csv(ref_data_clean, "ref_data5_clean.csv", row.names = F)
ref_data_clean = read.csv("ref_data5_clean.csv")

WOS_details = read.csv("WOS_references_search5_metareviews.csv")
colnames(WOS_details)[1] = "doi"
reference_details= merge(WOS_details, ref_data_clean, by = "doi")
write.csv(reference_details, "metareview_details.csv")

reference_details_short = reference_details[, c( "doi", "citation", "Publication.Year", "Source.Title", "Article.Title")]
reference_details_short = WOS_details[, c( "doi", "citation", "Publication.Year", "Source.Title", "Article.Title")]
write.csv(reference_details_short, "metareview_details_short.csv")


ref_ids = ref_data_clean[, c("article_id", "doi", "file_name")]
write.csv(ref_ids, "ref_ids.csv", row.names = F)
