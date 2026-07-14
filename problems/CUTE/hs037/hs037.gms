* GAMS-model hs037.dag.gms written by dag2gams Converter at 29/03/2004 16:58:58
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
objcon.. obj =e= -(x('1') * x('2') * x('3'));


con1..x('1') + 
2 * x('2') + 
2 * x('3') =g= 0;
con2..x('1') + 
2 * x('2') + 
2 * x('3') =l= 72;
x.lo('1')=0;
x.up('1')=42;
x.lo('2')=0;
x.up('2')=42;
x.lo('3')=0;
x.up('3')=42;
Model m/All/;
m.workspace = 32;
m.optfile = 1;options nlp=convert;
Solve m using nlp minimizing obj;
display x.l, obj.l;
  


