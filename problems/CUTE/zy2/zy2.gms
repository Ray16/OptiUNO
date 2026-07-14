* GAMS-model zy2.dag.gms written by dag2gams Converter at 29/03/2004 16:58:58
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
objcon.. obj =e= 11 * x('1') + 
x('2') + 
x('3') - 
6 * power(x('1'), 2) + 
power(x('1'), 3);


con1..power(x('1'), 2) + 
power(x('2'), 2) + 
power(x('3'), 2) =g= 4;
con2..power(x('1'), 2) + 
power(x('2'), 2) + 
power(x('3'), 2) =l= 10;
x.lo('1')=0;
x.lo('2')=0;
x.lo('3')=0;
x.up('3')=5;
Model m/All/;
m.workspace = 32;
m.optfile = 1;options nlp=convert;
Solve m using nlp minimizing obj;
display x.l, obj.l;
  


