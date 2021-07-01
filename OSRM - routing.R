#install.packages("osrm")
#remotes::install_github("riatelab/osrm")
#remotes::install_github("rCarto/osrm", force = T)
#install.packages("rJava")

pkgs <- c("osrm", "sp", "remotes", "rJava", "Runiversal")
sapply(pkgs, require, character.only = T) #load 

mode = "car"
mode = "bike"
mode = "foot"
#duration = minutes
#distance = meters

if(mode == "bike"){
  options(osrm.server = "http://127.0.0.1:5001/", osrm.profile = "bike")
  route <- osrmRoute(src = c(4.83, 52.36), dst = c(5.2, 53.26), overview = "full", returnclass = "sp")
} else if(mode == "foot"){
  options(osrm.server = "http://127.0.0.1:5002/", osrm.profile = "foot")
  route <- osrmRoute(src = c(4.83, 52.36), dst = c(5.2, 53.26), overview = "full", returnclass = "sp")
} else if(mode == "car"){
  options(osrm.server = "http://127.0.0.1:5000/", osrm.profile =  "car")
  route <- osrmRoute(src = c(4.83, 52.36), dst = c(5.2, 53.26), overview = "full", returnclass = "sp")
}

crs = "+init=EPSG:28992" #Amersfoort / RD New
route = spTransform(route, CRSobj = crs)
route
