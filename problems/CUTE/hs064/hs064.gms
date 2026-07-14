* GAMS-model hs064.dag.gms written by dag2gams Converter at 29/03/2004 16:58:58
* University of Vienna
$offdigit;
 Set i/1*1/;
 Set j/1*3/;
 Equations objcon
con1
;
Variables x(j), obj;
* Objective function (to be minimized) 
objcon.. obj =e= 50000 * (1/x('1')) + 
72000 * (1/x('2')) + 
144000 * (1/x('3')) + 
5 * x('1') + 
20 * x('2') + 
10 * x('3');


con1..4 * (1/x('1')) + 
32 * (1/x('2')) + 
120 * (1/x('3')) =l= 1;
x.lo('1')=1.0000000000000001e-05;
x.lo('2')=1.0000000000000001e-05;
x.lo('3')=1.0000000000000001e-05;
Model m/All/;
m.workspace = 32;
m.optfile = 1;options nlp=convert;
Solve m using nlp minimizing obj;
display x.l, obj.l;
  


