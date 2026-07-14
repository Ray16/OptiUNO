* GAMS-model bt7.dag.gms written by dag2gams Converter at 29/03/2004 17:00:0
* University of Vienna
$offdigit;
 Set i/1*3/;
 Set j/1*5/;
 Equations objcon
con1
con2
con3
;
Variables x(j), obj;
* Objective function (to be minimized) 
objcon.. obj =e= power((x('1')) - 1, 2) + 
100 * power(x('2') - 
power(x('1'), 2), 2);


con1.. x('1') + 
power(x('5'), 2) =e= 0.5;
con2.. -power(x('3'), 2) + 
x('1') * x('2') =e= 1;
con3.. x('1') + 
power(x('2'), 2) - 
power(x('4'), 2) =e= 0;
Model m/All/;
m.workspace = 32;
m.optfile = 1;options nlp=convert;
Solve m using nlp minimizing obj;
display x.l, obj.l;
  


