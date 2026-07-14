* GAMS-model allinitc.dag.gms written by dag2gams Converter at 29/03/2004 16:59:09
* University of Vienna
$offdigit;
 Set i/1*1/;
 Set j/1*4/;
 Equations objcon
con1
;
Variables x(j), obj;
* Objective function (to be minimized) 
objcon.. obj =e= power(power(x('2'), 2), 2) + 
power(x('1'), 2) * power(x('2'), 2) + 
power(sin(x('4')), 4) + 
2 * power(sin(x('3')), 2) + 
power(power(x('3'), 2) + 
power(x('1') + 
x('4'), 2), 2) + 
power(power(sin(x('4')), 2) + 
x('1') + 
power(x('2'), 2) * power(x('3'), 2) - 
4, 2) + 
x('3') + 
x('4') + 
power(x('1'), 2) + 
power(x('2'), 2) + 
power((x('4')) - 1, 2) + 
power(x('3') + 
x('4'), 2) - 4;


con1..power(x('1'), 2) + 
power(x('2'), 2) =l= 1;
x.lo('4')=2;
x.up('4')=2;
x.lo('3')=-10000000000;
x.up('3')=1;
x.lo('2')=1;
Model m/All/;
m.workspace = 32;
m.optfile = 1;options nlp=convert;
Solve m using nlp minimizing obj;
display x.l, obj.l;
  


