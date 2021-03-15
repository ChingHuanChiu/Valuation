# valuation


# Overview

There are two kinds of valuation method in valuation system, which are "Discount Cash Flow" and "Growth stock valuation", and use the estimate data from analysts on [Yahoo Finance](https://finance.yahoo.com/quote/AAPL/analysis?p=T) , such as 'Revenue', 'Growths' and 'EPS'

- DCF

    discount the free cash flow for 4 years and use 'wacc' as discount factor

    ![image](https://latex.codecogs.com/png.latex?value%20=%20\frac{FCF_1}{(1+wacc)}%20+%20....+\frac{FCF_n}{(1+wacc)^n}+\frac{FCF_n(1+g)}{wacc-g})
    
- Growth stock valuation

    ![image](https://latex.codecogs.com/png.latex?value%20=%20PE_{estimate}%20*%20EPS_{estimate})

    where ![image](https://latex.codecogs.com/png.latex?PE_{estimate}) is from a function of growth,  ![image](https://latex.codecogs.com/png.latex?PE_{estimate}=f(g))
