# valuation


# Overview

There are two kinds of valuation method in valuation system, which are "Discount Cash Flow" and "Growth stock valuation", and use the estimate data from analysts on [Yahoo Finance](https://finance.yahoo.com/quote/AAPL/analysis?p=T) , such as 'Revenue', 'Growths' and 'EPS'

- DCF

    discount the free cash flow for 4 years and use 'wacc' as discount factor

    $value = \frac{FCF_1}{(1+wacc)} + ....+\frac{FCF_n}{(1+wacc)^n}+\frac{FCF_n(1+g)}{wacc-g}$

- Growth stock valuation

    $value = PE_{estimate} * EPS_{estimate}$

    where $PE_{estimate}$  is from a function of growth,   $PE_{estimate}=f(g)$

    ![valuation%206af6ae5bd170453cba5d0acffc4324c6/image.jpg](valuation%206af6ae5bd170453cba5d0acffc4324c6/image.jpg)
