* GAMS-model hs054.dag.gms written by dag2gams Converter at 29/03/2004 17:00:0
* University of Vienna
$offdigit;
 Set i/1*1/;
 Set j/1*6/;
 Equations objcon
con1
;
Variables x(j), obj;
* Objective function (to be minimized) 
objcon.. obj =e= power(x('3'), 2) + 
power(x('4'), 2) + 
power(x('5'), 2) + 
power(x('6'), 2) + 
1.0416666666666667 * power(x('1'), 2) + 
1.0416666666666667 * power(x('2'), 2) + 
0.41666666666666674 * x('1') * x('2');


con1.. x('1') + 
0.5 * x('2') =e= 0.45000000000000001;
x.lo('1')=-1.25;
x.up('1')=1.25;
x.lo('2')=-11;
x.up('2')=9;
x.lo('3')=-0.2857142857142857;
x.up('3')=1.1428571428571428;
x.lo('4')=-0.20000000000000001;
x.up('4')=0.20000000000000001;
x.lo('5')=-20.019999999999996;
x.up('5')=19.98;
x.lo('6')=-0.20000000000000001;
x.up('6')=0.20000000000000001;
Model m/All/;
m.workspace = 32;
m.optfile = 1;options nlp=convert;
Solve m using nlp minimizing obj;
display x.l, obj.l;
  


