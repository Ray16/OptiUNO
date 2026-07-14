* GAMS-model pfit4.dag.gms written by dag2gams Converter at 29/03/2004 16:58:58
* University of Vienna
$offdigit;
 Set j/1*3/;
 Equations objcon
;
Variables x(j), obj;
* Objective function (to be minimized) 
objcon.. obj =e= power(((- ((- (x('3') + 
1)**((- (x('1') + 
2)))) + 
1) * (x('1') + 
1) * x('1') * x('2') * power(x('3'), 2))) + 239.670781893, 2) + 
power(((- (x('3') + 
1)**((- (x('1') + 
1)))) + 
1) * x('1') * x('2') * x('3') - 
(x('1') + 
1) * x('1') * x('2') * power(x('3'), 2) + 
216.09876543199999, 2) + 
power(-(((- (x('3') + 
1)**((- x('1')))) + 
1) * x('2')) + 
x('1') * x('2') * x('3') - 
0.5 * (x('1') + 
1) * x('1') * x('2') * power(x('3'), 2) + 
98.962962962899994, 2);


Model m/All/;
m.workspace = 32;
m.optfile = 1;options nlp=convert;
Solve m using nlp minimizing obj;
display x.l, obj.l;
  


