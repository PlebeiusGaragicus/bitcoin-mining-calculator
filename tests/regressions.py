import matplotlib.pyplot as plt
import numpy as np
from numpy import transpose
from numpy.linalg import inv
import random

random.seed(2019)

#print("\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n")

##########################################################################################
#----------------------------------------------Set up-------------------------------------
##########################################################################################

#Create some data points
x = np.array([-5, -4, -3, -2, -1, 0, 1, 2, 3, 4, 5])
y = np.array([20, 17, 10, 2, 2, 0, 1, 2, 9, 15, 25])
#y = [np.random.normal(i**3-i**2+i+4,8) for i in x]

#plot the data points
plt.scatter(x,y)
plt.show()

#Ask the user what power they'd like to use for the approximation
power = int(input("What power would you like to use for the approximation? : "))


##########################################################################################
#-------------Create X, XT and Y matrices so we can solve b = (XT.X)^-1.XT.Y--------------
##########################################################################################

#Create X matrix
X = np.empty((len(x), power+1))
#Fill X matrix
for i, row in enumerate(X):	
	for j in range(power+1):
		X[i,j] = x[i]**j

XT = transpose(X)
#Create Y matrix
Y = transpose([y])

#solve for b (y = b0 + b1*x + b2*x^2 + b3*x^3 + ... )
b = np.dot(np.dot(inv(np.dot(XT,X)),XT),y) 

##########################################################################################
#-------Create 100 x and y values for the regression curve, so that we can display it ----
##########################################################################################


x_reg = np.linspace(x[0], x[-1], num=100)

# we'll use the values contained in b to calculate y (y = b0 + b1*x + b2*x^2 + b3*x^3 + ... )
y_reg = np.empty((1,100)) #create empty y set
for i in range(100): #fill it up:
	y_reg[0,i] = 0 
	for j in range(power+1): #y_reg is the sum of the power coefficient * x to that power
		y_reg[0,i] += b[j]*x_reg[i]**j


##########################################################################################
#---------------------------------------Plot----------------------------------------------
##########################################################################################

#plot the data points
plt.scatter(x,y)
#plot the regression
plt.plot(x_reg,y_reg[0])
plt.show()
