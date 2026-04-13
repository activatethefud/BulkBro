import numpy as np
import math

class statlist:
        
        def __init__(self):
                self.data = []
                self.len = 0
                self.sum = 0
                self.var = 0
                self.std = 0
                self.avg = 0
                self.max = None
                self.min = None

        def append(self,val):
                
                self.data.append(val)
                                
                self.sum += val
                self.len += 1

                if self.max == None:
                        self.max = val
                else:
                        self.max = max(self.max,val)

                if self.min == None:
                        self.min = val
                else:
                        self.min = min(self.min,val)

                old_avg = self.avg

                self.avg = self.sum/self.len
                self.var += (val - old_avg)*(val - self.avg)

                self.max_abs = max(abs(self.max), abs(self.min))
                
                if self.len > 2:
                        self.std = math.sqrt(self.var/(self.len-1))
                
        
        def sum(self):
                return self.sum

        def len(self):
                return self.len

        def min(self):
                return self.min

        def max(self):
                return self.max

        def normalize(self,other):
                #return (other - self.avg)/self.std if self.std != 0 else 0
                return other/(self.max_abs + 0.01)
                #return abs((other-self.min)/(self.max + 0.01))

        def remove_outliers(self):
                pass

def load_sol(filename):
        import pickle
        return pickle.load(open(filename,'rb'))

def day_nutri(day):
        return sum(meal.nutri() for meal in day)
