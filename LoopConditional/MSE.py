import pandas as pd
import numpy as np
import scipy.optimize as opt
import time
import math
from scipy.optimize import differential_evolution
from geopy.distance import vincenty as vc
from scipy.stats import gaussian_kde


def intro():
    print("Well hello there! This program performs a Maximum Score Estimator. \n"
          +"You need to input the Excel file and provide the years in the "+
          "data.\n" +"Note that the program takes a while to compute the"+
          " coeffecients! ")
    main()

def main():
    filename = str(input(("Name of the file (Note: the file must be in the"+
                          " same folder as this program. And do not forget to"+
                          " add .xlsx or .xls at the end of the file name): ")))
    years = [int(x) for x in input('Years (Seperate with a space):').split()]

    print("The dataset you provided is:" + " " + filename ,
          "The years are:", years )
    restart = str(input("Do you wish to make adjustments? [y]Yes, [n]no, or"
                        + " [e]exit: "))
    if restart == 'y':
        main()
    elif restart == 'n':
        print("Alrighty then, the optimization is starting now. \n"
              +"Please sit back and relax, the process will take some time...")
        prob(filename, years)
    elif restart == 'e':
        exit()
    else:
        print("Error")
        exit()

def prob(filename, years):
    ps4_data = pd.read_excel(filename)
    ps4_data['pop_ths_log'] = np.log(ps4_data['population_target'] / 1000)
    ps4_data['price_ths_log'] = np.log(ps4_data['price'] / 1000)
    list1=['year','buyer_id', 'target_id','buyer_lat', 'buyer_long',
           'target_lat','target_long', 'num_stations_buyer',
           'corp_owner_buyer', 'pop_ths_log', 'price_ths_log' ]
    mat=ps4_data.as_matrix(columns= list1)


# Define a function to calculate the distance between buyer and target by
#indicating the row
# for the buyer and the row of the target. column 3 is the buyer's latitute
#in the matrix, and column 5 is the target's

# latitute in the matrix
    def distance_calc (dataset,rowb,rowt, yr):
        data = dataset[dataset[:,0] == yr]
        start = (data[rowb-1,3], data[rowb-1,4])
        stop = (data[rowt-1,5], data[rowt-1,6])
        return np.log(vc(start, stop).miles)

    def func(dataset,coef, bpos, tpos, yr):
    # So the function won't take observations from another year,
    #I have to create a temporary matrix based on a
    # specific year
        data = dataset[dataset[:,0] == yr]
        ob1 = data[bpos-1,7] * data[tpos-1,9]
        ob2 = data[bpos-1,8] * data[tpos-1,9]
        ob3 = distance_calc(data, bpos, tpos, yr)
        value = ob1 + coef[0] * ob2 + coef[1] * ob3
        return value


#This function creates a matrix of values "F(b,t)" for every combination of
#buyer and target per year
# Thus, the first element of the matrix is f(1,1) and the last is f(45,45)
#(for 2007) or f(54,54) (for 2008)
    def matrix(dataset, yr, coef):
        buyer_yr = dict()
        f_yr = np.empty
        all_buyers = []
        data = dataset[dataset[:,0] == yr]
        for b in data[:, 1]:
            buy=int(b)
            buyer_yr[buy] = []
            for t in data[:, 2]:
                tar=int(t)
                a = func(dataset, coef, buy, tar, yr)
                buyer_yr[buy].append(a)
            all_buyers.append(buyer_yr[buy])
        f_yr = np.stack(all_buyers)
        return(f_yr)

#This function creates a kernel function that has a limit of (0,1).
#First, you neeed to submit an array (i.e. a matrix
# with 1 row and n columns) that has each observation's value
#(f(b,t)+f(b',t')- f(b',t)-f(b,t')), which will be calculated

# inside the function (q))
    def kernel(x):
        b=gaussian_kde(x)
        result=b(x)
        return result


#This function returns the sum of " f(b,t)+f(b',t')- f(b',t)-f(b,t') "
#for each pair for both years

    def q(coef,dataset, years):

        rhs=[]

        for item in years:
            temp=matrix(dataset,item, coef).diagonal()
            for i in range(0, len(temp)-1):
                b1=temp[i]
                for j in range(1, len(temp)):
                    b2=temp[j]
                    if j> i:
                        s= b1+ b2
                        rhs.append(s)
        lhs=[]

        for item in years:
            temp=matrix(dataset,item, coef)
            for i in range(0, len(temp)-1):
                for j in range(1, len(temp)):
                    if j> i:
                        a= temp[i,j]
                        b=temp[j,i]
                        c= a+b
                        lhs.append(c)
        left=np.array(lhs)
        right=np.array(rhs)
        q = (left - right).reshape(1,2421)
        q_func=-(sum(kernel(q)))
        return q_func


#The optimization function

#Note: The optimization runs for a long time, just be patient!!!

    bnds = ((-50000, 50000),(-50000,50000))
    mse_results = differential_evolution(q, bnds ,args=(mat, years),
                                         maxiter = 100, tol = 0.001)

    print(mse_results)

intro()

def end():
    print("This program will close.")
    exit()
