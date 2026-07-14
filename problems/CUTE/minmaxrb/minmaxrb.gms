* GAMS-model minmaxrb.dag.gms written by dag2gams Converter at 29/03/2004 16:58:58
* University of Vienna
$offdigit;
 Set i/1*4/;
 Set j/1*3/;
 Equations objcon
con1
con2
con3
con4
;
Variables x(j), obj;
* Objective function (to be minimized) 
objcon.. obj =e= x('3');


con1..-x('1') + 
x('3') =g= -1;
con2..x('1') + 
x('3') =g= 1;
con3..(-10) * x('2') + 
x('3') + 
10 * power(x('1'), 2) =g= 0;
con4..10 * x('2') + 
x('3') - 
10 * power(x('1'), 2) =g= 0;
Model m/All/;
m.workspace = 32;
m.optfile = 1;options nlp=convert;
Solve m using nlp minimizing obj;
display x.l, obj.l;
  


