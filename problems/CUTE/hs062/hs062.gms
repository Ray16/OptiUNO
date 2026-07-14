* GAMS-model hs062.dag.gms written by dag2gams Converter at 29/03/2004 16:58:58
* University of Vienna
$offdigit;
 Set i/1*1/;
 Set j/1*3/;
 Equations objcon
con1
;
Variables x(j), obj;
* Objective function (to be minimized) 
objcon.. obj =e= (-9330.4599999999991) * log((x('3') + 
0.029999999999999999) / (0.13 * x('3') + 
0.029999999999999999)) - 
9008.7199999999993 * log((x('2') + 
x('3') + 
0.029999999999999999) / (0.070000000000000007 * x('2') + 
x('3') + 
0.029999999999999999)) - 
8204.369999999999 * log((x('1') + 
x('2') + 
x('3') + 
0.029999999999999999) / (0.089999999999999997 * x('1') + 
x('2') + 
x('3') + 
0.029999999999999999));


con1.. x('1') + 
x('2') + 
x('3') =e= 1;
x.lo('1')=0;
x.up('1')=1;
x.lo('2')=0;
x.up('2')=1;
x.lo('3')=0;
x.up('3')=1;
Model m/All/;
m.workspace = 32;
m.optfile = 1;options nlp=convert;
Solve m using nlp minimizing obj;
display x.l, obj.l;
  


