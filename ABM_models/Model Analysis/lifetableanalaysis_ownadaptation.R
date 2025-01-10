setwd("D:/PhD EXPANSE/Data/Amsterdam/Health impact")
# setwd("C:/Current/Tabea/HealthImpact")


library(stats)
# definition of helper functions
logit <- function(p){log(p/(1-p))}
expit <- function(x){exp(1/(1+exp(-x)))}
Prob2Rate <- function(prob,t=1) {-log(1-prob)/t}
Rate2Prob <- function(rate,t=1) {1-exp(-rate*t)}

## NO2 relative risk function
NO2RR <- function(expo,ref=0) {
  beta.NO2 <- log(1.02)/10
  exp(beta.NO2*(expo - ref))
}

# data from https://bjsm.bmj.com/content/57/15/979, https://shiny.mrc-epid.cam.ac.uk/meta-analyses-physical-activity/
METhriskvals = read.csv("total-population-all-cause-mortality-fatal-q-0.75.csv")
METhriskvals <- METhriskvals[,c("dose", "RR")]


## MET relative risk function
METlogRR <- splinefun(METhriskvals$dose,log(METhriskvals$RR))
METRR <- function(expo,ref=0) {
  ifelse(expo==ref,1,exp(METlogRR(expo)) / exp(METlogRR(ref)))
}

life.expectancy <- function(mortality.rates,start.age=0) {
  ages <- start.age + 1:length(mortality.rates) - 1
  prob.death <- Rate2Prob(mortality.rates)
  S <- c(1,cumprod(1-prob.death))
  sum(-diff(S) * ages)
}
stats <- function(x,na.rm=TRUE){if (na.rm) {x <- na.omit(x)}; c(n=length(x),mean=mean(x),sd=sd(x),median=median(x),min=min(x),max=max(x))}


# Read in mortality rates
load("NL_2021_rates_males.Rdata")
male.mort.pred <- mort.pred
life.expectancy(male.mort.pred$expected,start.age=min(male.mort.pred$age))
load("NL_2021_rates_females.Rdata")
female.mort.pred <- mort.pred
life.expectancy(female.mort.pred$expected,start.age=min(female.mort.pred$age))

# First need to estimate a reference exposure value for which the average expected mortality is equal to the observed values
# Use numerical optimization to estimate the value that minimizes the discrepancy between the average RR and 1
opt.funNO2 <- function(ref){
NO2RR <- NO2RR(baseline.NO2exposures,ref)
abs(mean(NO2RR) - 1)
}

opt.funMET <- function(ref){
METRR <- METRR(baseline.METexposures,ref)
abs(mean(METRR) - 1)
}

populationsubsets <- as.vector(0:9)
# populationsubsets<- c(0:1)
print(populationsubsets)

scenarios <- c("15mCityWithDestination", "15mCity", "PrkPriceInterv", "NoEmissionZone2030", "NoEmissionZone2025")


meanNO2LEGainsCrossPop <- c()
meanMETLEGainsCrossPop <- c()

for (popindex in seq_along(populationsubsets)) {
  print(paste("popsample", popindex))

  meanNO2LEGains <- c()
  meanMETLEGains <- c()
  # Read in the data
  data <- read.csv(paste0("Amsterdam_population_subset21750_",populationsubsets[popindex], "_exposure.csv"))

  head(data)
  table(data$age)

  #######################################
  ################# NO2 #################
  #######################################
  baseline.NO2exposure <- "NO2_StatusQuo"
  baseline.NO2exposures <- data[,baseline.NO2exposure]

  # Do we need age-specific values?
  plot(sort(unique(data$age)),sapply(sort(unique(data$age)),function(cur.age){
    baseline.NO2exposures <- subset(data,age==cur.age)[,baseline.NO2exposure]
    init <- mean(baseline.NO2exposures)
    ref <- optim(par=init,opt.funNO2,method="Brent",lower=min(baseline.NO2exposures)-1e-6,upper=max(baseline.NO2exposures)+1e-6)$par
    ref
  }),ylab="Estimated reference value")
  # Doesn't seem to be the case (very little data at ages over 95), so we can use a single reference value
  init <- mean(baseline.NO2exposures)
  ref.NO2 <- optim(par=init,opt.funNO2,method="Brent",lower=min(baseline.NO2exposures),upper=max(baseline.NO2exposures))$par
  ref.NO2
  # Look at the distribution of estimated relative risks for baseline exposures
  stats(NO2RR(baseline.NO2exposures,ref.NO2))
  hist(NO2RR(baseline.NO2exposures,ref.NO2))

  # Estimate mortality rates for each subject until end of life
  baseline.NO2mortality.rates <- lapply(1:nrow(data),function(ix){
    subject.age <- data$age[ix]
    if (data$sex[ix]=="female") {
      mort.pred <- female.mort.pred
    } else {
      mort.pred <- male.mort.pred
    }
    if (subject.age == 0) {
      rates <- c(mort.pred$expected[1],mort.pred$expected,Inf)
    } else if (subject.age > max(mort.pred$age)) {
      rates <- Inf
    } else {
      rates <- c(mort.pred$expected[subject.age:max(mort.pred$age)],Inf)
    }
    names(rates) <- subject.age:(subject.age+length(rates)-1)
    rates <- NO2RR(data[ix,baseline.NO2exposure],ref.NO2)*rates
    rates
  })
  # Use these to estimate individiual life expectancies
  baseline.NO2life.expectancies <- sapply(baseline.NO2mortality.rates,function(mortality.rates){
    life.expectancy(mortality.rates,start.age=as.numeric(names(mortality.rates))[1])
  })
  # Look at the distribution of life expectancy
  hist(baseline.NO2life.expectancies)
  plot(data$age,baseline.NO2life.expectancies)
  abline(a=0,b=1)
  # Look at the distribution of expected remaining years of life
  hist(baseline.NO2life.expectancies-data$age)
  plot(data$age,baseline.NO2life.expectancies - data$age)
  data[, c("StatusQuoNO2LifeExpectancy")] <- baseline.NO2life.expectancies

  #######################################
  ################# MET #################
  #######################################

  baseline.METexposure <- "totalMEThwk_StatusQuo"
  baseline.METexposures <- data[,baseline.METexposure]

  # repeat for MET
  plot(sort(unique(data$age)),sapply(sort(unique(data$age)),function(cur.age){
    baseline.METexposures <- subset(data,age==cur.age)[,baseline.METexposure]
    init <- mean(baseline.METexposures)
    ref <- optim(par=init,opt.funMET,method="Brent",lower=min(baseline.METexposures)-1e-6,upper=max(baseline.METexposures)+1e-6)$par
    ref
  }),ylab="Estimated reference value")
  # Doesn't seem to be the case (very little data at ages over 95), so we can use a single reference value
  # select the non Nan minimum and maximum values
  init <- mean(baseline.METexposures)
  ref.MET <- optim(par=init,opt.funMET,method="Brent",lower=min(baseline.METexposures),upper=max(baseline.METexposures))$par
  ref.MET
  # Look at the distribution of estimated relative risks for baseline exposures
  stats(METRR(baseline.METexposures,ref.MET))
  hist(METRR(baseline.METexposures,ref.MET))

  # Estimate mortality rates for each subject until end of life
  baseline.METmortality.rates <- lapply(1:nrow(data),function(ix){
    subject.age <- data$age[ix]
    if (data$sex[ix]=="female") {
      mort.pred <- female.mort.pred
    } else {
      mort.pred <- male.mort.pred
    }
    if (subject.age == 0) {
      rates <- c(mort.pred$expected[1],mort.pred$expected,Inf)
    } else if (subject.age > max(mort.pred$age)) {
      rates <- Inf
    } else {
      rates <- c(mort.pred$expected[subject.age:max(mort.pred$age)],Inf)
    }
    names(rates) <- subject.age:(subject.age+length(rates)-1)
    rates <- METRR(data[ix,baseline.METexposure],ref.MET)*rates
    rates
  })
  # Use these to estimate individiual life expectancies
  baseline.METlife.expectancies <- sapply(baseline.METmortality.rates,function(mortality.rates){
    life.expectancy(mortality.rates,start.age=as.numeric(names(mortality.rates))[1])
  })
  # Look at the distribution of life expectancy
  hist(baseline.METlife.expectancies)
  plot(data$age,baseline.METlife.expectancies)
  abline(a=0,b=1)
  # Look at the distribution of expected remaining years of life
  hist(baseline.METlife.expectancies-data$age)
  plot(data$age,baseline.METlife.expectancies - data$age)
  data[, c("StatusQuoMETLifeExpectancy")] <- baseline.METlife.expectancies

  columnnames <- colnames(data)

  for (scenario in scenarios) {
      intervention.NO2exposure <- paste0("NO2_", scenario)
      intervention.METexposure <- paste0("totalMEThwk_", scenario)

      print(paste("NO2", "baseline", mean(baseline.NO2exposures), scenario, mean(data[,intervention.NO2exposure])))
      print(paste("METh/week","baseline", mean(baseline.METexposures), scenario, mean(data[,intervention.METexposure])))

      #######################################
      ################# NO2 #################
      #######################################
      # Estimate mortality rates after intervention
      intervention.mortality.NO2rates <- lapply(1:nrow(data),function(ix){
        subject.age <- data$age[ix]
        if (data$sex[ix]=="female") {
          mort.pred <- female.mort.pred
        } else {
          mort.pred <- male.mort.pred
        }
        if (subject.age == 0) {
          rates <- c(mort.pred$expected[1],mort.pred$expected,Inf)
        } else if (subject.age > max(mort.pred$age)) {
          rates <- Inf
        } else {
          rates <- c(mort.pred$expected[subject.age:max(mort.pred$age)],Inf)
        }
        names(rates) <- subject.age:(subject.age+length(rates)-1)
        rates <- NO2RR(data[ix,intervention.NO2exposure],ref.NO2)*rates
        rates
      })
      # Use these to estimate individiual life expectancies
      intervention.NO2life.expectancies <- sapply(intervention.mortality.NO2rates,function(mortality.rates){
        life.expectancy(mortality.rates,start.age=as.numeric(names(mortality.rates))[1])
      })

      ## report results for NO2
      # Compare to life expectancy without intervention
      head(cbind(baseline.NO2life.expectancies,intervention.NO2life.expectancies))
      # Only in rare occasions is the life expectancy shorter after intervention
      table(baseline.NO2life.expectancies <= intervention.NO2life.expectancies)
      data[which(baseline.NO2life.expectancies > intervention.NO2life.expectancies),c(baseline.NO2exposure,intervention.NO2exposure)]

      plot(baseline.NO2life.expectancies,intervention.NO2life.expectancies)
      title(main=paste0(scenario, " NO2 exposure"), sub="Life expectancy without intervention vs with intervention")
      # save the plot

      abline(a=0,b=1,col="red")
      # Look at the distribution of years of life gained (or lost)
      hist(intervention.NO2life.expectancies-baseline.NO2life.expectancies)
      stats(intervention.NO2life.expectancies-baseline.NO2life.expectancies)
      data[, c(paste0(scenario, "NO2LifeExpectancy"))] <- intervention.NO2life.expectancies
      data[, c(paste0(scenario, "NO2LifeExpectancyGain"))] <- intervention.NO2life.expectancies - baseline.NO2life.expectancies
      meanNO2LEGains <- c(meanNO2LEGains, mean(intervention.NO2life.expectancies-baseline.NO2life.expectancies))

      #######################################
      ################# MET #################
      #######################################
      # Estimate mortality rates after intervention
      intervention.mortality.METrates <- lapply(1:nrow(data),function(ix){
        subject.age <- data$age[ix]
        if (data$sex[ix]=="female") {
          mort.pred <- female.mort.pred
        } else {
          mort.pred <- male.mort.pred
        }
        if (subject.age == 0) {
          rates <- c(mort.pred$expected[1],mort.pred$expected,Inf)
        } else if (subject.age > max(mort.pred$age)) {
          rates <- Inf
        } else {
          rates <- c(mort.pred$expected[subject.age:max(mort.pred$age)],Inf)
        }
        names(rates) <- subject.age:(subject.age+length(rates)-1)
        rates <- METRR(data[ix,intervention.METexposure],ref.MET)*rates
        rates
      })
      # Use these to estimate individiual life expectancies
      intervention.METlife.expectancies <- sapply(intervention.mortality.METrates,function(mortality.rates){
        life.expectancy(mortality.rates,start.age=as.numeric(names(mortality.rates))[1])
      })

      ## report results for MET
      # Compare to life expectancy without intervention
      head(cbind(baseline.METlife.expectancies,intervention.METlife.expectancies))
      # Only in rare occasions is the life expectancy shorter after intervention
      table(baseline.METlife.expectancies <= intervention.METlife.expectancies)
      data[which(baseline.METlife.expectancies > intervention.METlife.expectancies),c(baseline.METexposure,intervention.METexposure)]

      plot(baseline.METlife.expectancies,intervention.METlife.expectancies)
      title(main=paste0(scenario, " MET exposure"), sub="Life expectancy without intervention vs with intervention")
      # save the plot

      abline(a=0,b=1,col="red")
      # Look at the distribution of years of life gained (or lost)
      hist(intervention.METlife.expectancies-baseline.METlife.expectancies)
      stats(intervention.METlife.expectancies-baseline.METlife.expectancies)
      data[, c(paste0(scenario, "METhLifeExpectancy"))] <- intervention.METlife.expectancies
      data[, c(paste0(scenario, "METhLifeExpectancyGain"))] <- intervention.METlife.expectancies - baseline.METlife.expectancies
      meanMETLEGains <- c(meanMETLEGains, mean(intervention.METlife.expectancies-baseline.METlife.expectancies))

    
  }
  write.csv(data, file = paste0("Amsterdam_population_subset21750_", populationsubsets[popindex], "_exposure_LifeExpectancyGains.csv"))
  meanNO2LEGainsCrossPop[[popindex]] <- meanNO2LEGains
  meanMETLEGainsCrossPop[[popindex]] <- meanMETLEGains
}

# make a dataframe of the mean life expectancy gains, the population subset and the scenario
df <- data.frame(popsamples = populationsubsets)
df[paste0(scenarios, "NO2LEGain")] <- NA
df[paste0(scenarios, "METhLEGain")] <- NA
for (i in 1:length(populationsubsets)) {
    df[i, paste0(scenarios, "NO2LEGain")] <- meanNO2LEGainsCrossPop[[i]]
    df[i, paste0(scenarios, "METhLEGain")] <- meanMETLEGainsCrossPop[[i]]
}
colnames <- c(paste0(scenarios, "NO2LEGain") , paste0(scenarios, "METhLEGain"))
df[colnames] <- lapply(df[colnames], function(x) as.numeric(as.character(x)))
scenarios_standardized = paste0(colnames, "_standardized")
df[scenarios_standardized] <- df[colnames]
scenarios_totpop = paste0(colnames, "_totpop")
df[scenarios_totpop] <- df[colnames]
df[scenarios_standardized] <- df[scenarios_standardized]*100000
df[scenarios_totpop] <- df[scenarios_totpop]*872754

df[length(populationsubsets)+1,] <- c("mean", colMeans(df[,-1], na.rm = TRUE))
write.csv(df, file = "Amsterdam_population_subset21750_meanLEGainsCrossPopNEW.csv", row.names = FALSE)









