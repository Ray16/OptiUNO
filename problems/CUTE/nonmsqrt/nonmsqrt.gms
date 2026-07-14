* GAMS-model nonmsqrt.dag.gms written by dag2gams Converter at 29/03/2004 17:01:1
* University of Vienna
$offdigit;
 Set j/1*9/;
 Equations objcon
;
Variables x(j), obj;
* Objective function (to be minimized) 
objcon.. obj =e= power(power(x('1'), 2) + 
x('1') * x('2') + 
x('1') * x('3') - 
0.92595936673312118, 2) + 
power(power(x('2'), 2) + 
x('1') * x('2') + 
x('2') * x('3') + 
0.15750346905483398, 2) + 
power(power(x('4'), 2) + 
x('4') * x('5') + 
x('4') * x('6') + 
0.20415777958403747, 2) + 
power(power(x('5'), 2) + 
x('4') * x('5') + 
x('5') * x('6') + 
0.67705943508713184, 2) + 
power(power(x('7'), 2) + 
x('7') * x('8') + 
x('7') * x('9') + 
0.26487854781507608, 2) + 
power(power(x('8'), 2) + 
x('7') * x('8') + 
x('8') * x('9') + 
0.7012804121709143, 2) + 
power(power(x('3'), 2) + 
x('2') * x('3') + 
x('1') * x('3') - 
0.83777797264094944, 2) + 
power(power(x('6'), 2) + 
x('5') * x('6') + 
x('4') * x('6') - 
0.63732298096217632, 2) + 
power(power(x('9'), 2) + 
x('8') * x('9') + 
x('7') * x('9') + 
0.51570348396953092, 2);


Model m/All/;
m.workspace = 32;
m.optfile = 1;options nlp=convert;
Solve m using nlp minimizing obj;
display x.l, obj.l;
  


