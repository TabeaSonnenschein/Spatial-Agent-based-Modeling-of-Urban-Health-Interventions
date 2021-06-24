#install.packages("osrm")
remotes::install_github("riatelab/osrm")

install.packages("remotes")

require("osrm")
require("remotes")
install.packages("rJava")
library(osrm)


options(osrm.server = "http://0.0.0.0:5000/",  osrm.profile = "car")


locations = data.frame(comm_id = c("A", "B", "C"), lon = c(52.36, 53.26, 52.76),  lat = c(4.83, 5.2, 4.32))

osrmTable(loc = locations)


route <- osrmRoute(src = c(52.36, 4.83), dst = c(53.26, 5.2), overview = "full", returnclass = "sf")
