
use "/Users/EyadsMacPro/Google Drive/PhD/Python/CompEcon_Fall17/Functions/PS3_data.dta", clear

keep if hannhrs>0 & hannhrs !=. & hlabinc !=. & hyrsed !=. & age !=. & hrace !=.

gen wageperhour = hlabinc/hannhrs
gen logwage= log(wageperhour)

keep if hsex==1 & age >=25 & age <=60 & wageperhour >7


gen Black = 1 if hrace==2
replace Black=0 if missing(Black)

gen Hispanic =1 if hrace==5
replace Hispanic=0 if missing(Hispanic)

gen Other = 1 if hrace==3 | hrace==4 | hrace >=6
replace Other=0 if missing(Other)

keep if year==1971


reg logwage hyrsed age Black Hispanic Other



program olsviaml
        version 8.0
        args lnf theta1
        quietly replace `lnf' = ln(normden($ML_y1-`theta1'))
end


ml model lf olsviaml (logwage = hyrsed age Black Hispanic Other)
ml maximize
