# valuation


# Overview

There are two kinds of valuation method in valuation system, which are "Discount Cash Flow" and "Growth stock valuation" and use the estimate data from analysts on [Yahoo Finance](https://finance.yahoo.com/quote/AAPL/analysis?p=T) , such as 'Revenue', 'Growths' and 'EPS'

- DCF

    discount the free cash flow for 4 years and use 'wacc' as discount factor

    ![image](https://latex.codecogs.com/png.latex?value%20=%20\frac{FCF_1}{(1+wacc)}%20+%20....+\frac{FCF_n}{(1+wacc)^n}+\frac{FCF_n(1+g)}{wacc-g})
    
- Growth stock valuation

    ![image](https://latex.codecogs.com/png.latex?value%20=%20PE_{estimate}%20*%20EPS_{estimate})

    where ![image](https://latex.codecogs.com/png.latex?PE_{estimate}) is  the function of growth rate, which is to find the relationship between "Growth" and "PE ratio"
    ![image](https://latex.codecogs.com/png.latex?PE_{estimate}=f(g)), namely 
                           

    ![image](https://user-images.githubusercontent.com/51486531/111328633-5f378080-86a9-11eb-9758-5d580b48ef7b.png)

    
    
![image](https://user-images.githubusercontent.com/51486531/111170186-a147c000-85de-11eb-842b-1bb81a704e24.jpg)

# USAGE
`res = Valuation('AAPL').value()`

`res = {'DCF法:': '94.18元', '成長型股票評價:': '147.42元'}`
