
pkgs <- c("sf", "sp", "stplanr", "rgdal", "igraph")
sapply(pkgs, require, character.only = T) #load 
rm(pkgs)

city = "Amsterdam"

setwd("C:/Dokumente/PhD EXPANSE/Data/Amsterdam/case study/data/final model data")

if(city == "Utrecht"){
  dsn <- "C:/Dokumente/PhD EXPANSE/Courses/Spatial Data Analysis and Simulation Modeling/case study/data/final model data"
  Streets <- readOGR(dsn=dsn ,layer="Utrecht_busy streets")
  
}
if(city == "Amsterdam"){
  dsn_data <- "C:/Dokumente/PhD EXPANSE/Data/Amsterdam/Built Environment/Transport Infrastructure/cars"
  #Streets <- readOGR(dsn=dsn_data ,layer="Car Traffic_ED50window")
  Streets <- readOGR(dsn=dsn_data ,layer="Car Traffic_ED50window_small")
  #Streets <- readOGR(dsn=dsn_data ,layer="Car Traffic")
  dsn_data <- "C:/Dokumente/PhD EXPANSE/Data/Amsterdam/Built Environment/Transport Infrastructure/bike"
  BikeLanes = readOGR(dsn=dsn_data ,layer="Bike_Network_ED50_ small_window")
  crs <- "+init=EPSG:23095" #ED_1950_TM_5_NE
}


proj4string(Streets)= CRS(crs)
Street_Line_network <- SpatialLinesNetwork(Streets)
nr_streets <- length(Street_Line_network@sl@lines)
Street_data <- Streets@data
Street_data$street_length = st_length(st_as_sf(Streets))

plot(Street_Line_network)



#Identifying start and endpoints of streets
Street_data$startpoint_x <- ""
Street_data$startpoint_y <- ""
Street_data$endpoint_x <- ""
Street_data$endpoint_y <- ""
coords= coordinates(Streets)
for (i in 1:nrow(Street_data)){
  Street_data$startpoint_x[i] <- coords[[i]][[1]][1,1]
  Street_data$startpoint_y[i] <- coords[[i]][[1]][1,2]
  n <- nrow(coords[[i]][[1]])
  Street_data$endpoint_x[i] <- coords[[i]][[1]][n,1]
  Street_data$endpoint_y[i] <- coords[[i]][[1]][n,2]
}

# Creating a unique Nodes point dataset
O <- Street_data[, c("startpoint_x", "startpoint_y")]
D <- Street_data[, c("endpoint_x", "endpoint_y")]
colnames(O) <- c("x", "y") 
colnames(D) <- c("x", "y") 
Nodes <- rbind(O, D)
Nodes <- unique(Nodes)
Nodes$ID <- ""
for (i in 1:nrow(Nodes)){
  Nodes$ID[i] <- paste("Node_", i, sep = "")
}

Street_data = merge(Street_data,  Nodes, by.x= c("startpoint_x", "startpoint_y"), by.y = c("x", "y"), all.x = T, all.y = F)
Street_data = merge(Street_data,  Nodes, by.x= c("endpoint_x", "endpoint_y"), by.y = c("x", "y"), all.x = T, all.y = F)
Edge_list = Street_data[,c("ID.x", "ID.y")]
Edge_list = unique(Edge_list)
Edge_list$length = ""
Edge_list$average_Nrcars = ""
for (i in 1:nrow(Edge_list)){
  x <- merge(Street_data, Edge_list[i,], by= c("ID.x", "ID.y"), all.x = F)
  Edge_list$length[i] = sum(x$street_length)
  Edge_list$average_Nrcars[i] = mean(as.numeric(as.character(x$etmaal)))
}

write.csv(Edge_list, paste("Edge_list_", city, ".csv", sep = ""))
write.csv(Street_data, paste("Street_data_", city, ".csv", sep = ""))


write.csv(Nodes, paste("Street_Nodes_", city, ".csv", sep = ""))
Nodes = read.csv(paste("Street_Nodes_", city, ".csv", sep = ""))

options(digits=17)
x <- as.numeric(Nodes$x)
y <-  as.numeric(Nodes$y)
str(x)
x
coordinates(Nodes)= ~ x + y
proj4string(Nodes)= CRS(crs)
writeOGR(Nodes, dsn=dsn,layer=paste("Street_Nodes_", city, sep = ""),driver="ESRI Shapefile")

# Visualize the results
plot(Streets)
plot(Nodes, add = T)

Nodes = read.csv(paste("Street_Nodes_", city, ".csv", sep = ""))
# Create and Origin Destination Matrix with routes through Nodes
OD_matrix <- as.data.frame(matrix(nrow = nrow(Nodes), ncol = nrow(Nodes)))
colnames(OD_matrix) = Nodes$ID
rownames(OD_matrix) = Nodes$ID

street_network <- graph_from_data_frame(Edge_list[,c("ID.x", "ID.y")], directed = F)
Nodes$ID = as.character(Nodes$ID)


for(O in 1:nrow(Nodes)){
  for(D in 1:nrow(Nodes)){
    x <-(shortest_paths(street_network, from = Nodes$ID[O], to = Nodes$ID[D]))
    OD_matrix[D,O] = paste(names(x$vpath[[1]]), collapse =  "\" \"")
    OD_matrix[D,O] = paste("[\"", OD_matrix[D,O], "\"]", sep = "")
  }
}



for(O in 1:nrow(OD_matrix)){
  for(D in 1:nrow(OD_matrix)){
    OD_matrix[O, D] = gsub(", ", ") (", OD_matrix[O,D])
    OD_matrix[O, D] = paste("[(", OD_matrix[O,D], ")]", sep = "")
  }
}

# 
# for(O in 1752:nrow(Nodes)){
#   for(D in 1:nrow(Nodes)){
#     x <-(shortest_paths(street_network, from = Nodes$ID[O], to = Nodes$ID[D]))
#     OD_matrix[D,O] = paste(names(x$vpath[[1]]), collapse =  ", ")
#   }
# }

write.csv(OD_matrix, paste("OD_Matrix_", city, ".csv", sep = ""))



x <-(shortest_paths(street_network, from = Nodes$ID[O], to = Nodes$ID[D]))
paste(names(x$vpath[[1]]), collapse =  ", ")

Nodes$ID[O]

x <- sample.int(nrow(OD_matrix), 500)
x

test = OD_matrix[x,x]
for(O in 1:nrow(test)){
  for(D in 1:nrow(test)){
    test[O, D] = gsub(") (", "\" \"", test[O,D])
  }
}

x = which(test[,1] == "[()]")

test = test[-c(x), -c(x)]

write.csv(test, paste("sample_OD_Matrix_", city, ".csv", sep = ""))

