* GAMS-model bt5.dag.gms written by dag2gams Converter at 29/03/2004 16:58:58
* University of Vienna
$offdigit;
 Set i/1*2/;
 Set j/1*3/;
 Equations objcon
con1
con2
;
Variables x(j), obj;
* Objective function (to be minimized) 
objcon.. obj =e= -(power(x('1'), 2) + 
power(x('3'), 2) + 
2 * power(x('2'), 2) + 
x('1') * x('2') + 
x('1') * x('3')) - 1000;


con1.. 8 * x('1') + 
14 * x('2') + 
7 * x('3') =e= 56;
con2.. power(x('1'), 2) + 
power(x('3'), 2) + 
power(x('2'), 2) =e= 25;
Model m/All/;
m.workspace = 32;
m.optfile = 1;options nlp=convert;
Solve m using nlp minimizing obj;
display x.l, obj.l;
  


