* GAMS-model polak2.dag.gms written by dag2gams Converter at 29/03/2004 16:59:02
* University of Vienna
$offdigit;
 Set i/1*2/;
 Set j/1*11/;
 Equations objcon
con1
con2
;
Variables x(j), obj;
* Objective function (to be minimized) 
objcon.. obj =e= x('11');


con1..exp(power(x('3'), 2) + 
power(x('5'), 2) + 
power(x('6'), 2) + 
power(x('7'), 2) + 
power(x('8'), 2) + 
power(x('9'), 2) + 
power(x('10'), 2) + 
1e-08 * power(x('1'), 2) + 
power((x('2')) + 2, 2) + 
4 * power(x('4'), 2)) - 
x('11') =l= 0;
con2..exp(power(x('3'), 2) + 
power(x('5'), 2) + 
power(x('6'), 2) + 
power(x('7'), 2) + 
power(x('8'), 2) + 
power(x('9'), 2) + 
power(x('10'), 2) + 
1e-08 * power(x('1'), 2) + 
4 * power(x('4'), 2) + 
power((x('2')) - 2, 2)) - 
x('11') =l= 0;
Model m/All/;
m.workspace = 32;
m.optfile = 1;options nlp=convert;
Solve m using nlp minimizing obj;
display x.l, obj.l;
  


