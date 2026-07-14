* GAMS-model hatfldf.dag.gms written by dag2gams Converter at 29/03/2004 16:58:58
* University of Vienna
$offdigit;
 Set i/1*3/;
 Set j/1*3/;
 Equations objcon
con1
con2
con3
;
Variables x(j), obj;
* Objective function (to be minimized) 
objcon.. obj =e= 0;


con1.. exp(x('2')) * x('1') + 
x('3') =e= 0.032000000000000001;
con2.. exp(2 * x('2')) * x('1') + 
x('3') =e= 0.056000000000000001;
con3.. exp(3 * x('2')) * x('1') + 
x('3') =e= 0.099000000000000005;
Model m/All/;
m.workspace = 32;
m.optfile = 1;options nlp=convert;
Solve m using nlp minimizing obj;
display x.l, obj.l;
  


