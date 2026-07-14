* GAMS-model vanderm4.dag.gms written by dag2gams Converter at 29/03/2004 17:01:1
* University of Vienna
$offdigit;
 Set i/1*17/;
 Set j/1*9/;
 Equations objcon
con1
con2
con3
con4
con5
con6
con7
con8
con9
con10
con11
con12
con13
con14
con15
con16
con17
;
Variables x(j), obj;
* Objective function (to be minimized) 
objcon.. obj =e= 0;


con1..-x('8') + 
x('9') =g= 0;
con2..-x('7') + 
x('8') =g= 0;
con3..-x('6') + 
x('7') =g= 0;
con4..-x('5') + 
x('6') =g= 0;
con5..-x('4') + 
x('5') =g= 0;
con6..-x('3') + 
x('4') =g= 0;
con7..-x('2') + 
x('3') =g= 0;
con8..-x('1') + 
x('2') =g= 0;
con9.. power(x('1') + 
x('2') + 
x('3') + 
x('4') + 
x('5') + 
x('6') + 
x('7') + 
x('8') + 
x('9') - 
1.99609375, 2) =e= 0;
con10.. power(power(x('1'), 2) + 
power(x('2'), 2) + 
power(x('3'), 2) + 
power(x('4'), 2) + 
power(x('5'), 2) + 
power(x('6'), 2) + 
power(x('7'), 2) + 
power(x('8'), 2) + 
power(x('9'), 2) - 
1.3333282470703125, 2) =e= 0;
con11.. power(power(x('1'), 3) + 
power(x('2'), 3) + 
power(x('3'), 3) + 
power(x('4'), 3) + 
power(x('5'), 3) + 
power(x('6'), 3) + 
power(x('7'), 3) + 
power(x('8'), 3) + 
power(x('9'), 3) - 
1.1428571343421936, 2) =e= 0;
con12.. power(power(x('1'), 9) + 
power(x('2'), 9) + 
power(x('3'), 9) + 
power(x('4'), 9) + 
power(x('5'), 9) + 
power(x('6'), 9) + 
power(x('7'), 9) + 
power(x('8'), 9) + 
power(x('9'), 9) - 
1.0019569471624266, 2) =e= 0;
con13.. power(power(x('1'), 8) + 
power(x('2'), 8) + 
power(x('3'), 8) + 
power(x('4'), 8) + 
power(x('5'), 8) + 
power(x('6'), 8) + 
power(x('7'), 8) + 
power(x('8'), 8) + 
power(x('9'), 8) - 
1.003921568627451, 2) =e= 0;
con14.. power(power(x('1'), 4) + 
power(x('2'), 4) + 
power(x('3'), 4) + 
power(x('4'), 4) + 
power(x('5'), 4) + 
power(x('6'), 4) + 
power(x('7'), 4) + 
power(x('8'), 4) + 
power(x('9'), 4) - 
1.0666666666511446, 2) =e= 0;
con15.. power(power(x('1'), 7) + 
power(x('2'), 7) + 
power(x('3'), 7) + 
power(x('4'), 7) + 
power(x('5'), 7) + 
power(x('6'), 7) + 
power(x('7'), 7) + 
power(x('8'), 7) + 
power(x('9'), 7) - 
1.0078740157480315, 2) =e= 0;
con16.. power(power(x('1'), 5) + 
power(x('2'), 5) + 
power(x('3'), 5) + 
power(x('4'), 5) + 
power(x('5'), 5) + 
power(x('6'), 5) + 
power(x('7'), 5) + 
power(x('8'), 5) + 
power(x('9'), 5) - 
1.0322580645160997, 2) =e= 0;
con17.. power(power(x('1'), 6) + 
power(x('2'), 6) + 
power(x('3'), 6) + 
power(x('4'), 6) + 
power(x('5'), 6) + 
power(x('6'), 6) + 
power(x('7'), 6) + 
power(x('8'), 6) + 
power(x('9'), 6) - 
1.0158730158730158, 2) =e= 0;
Model m/All/;
m.workspace = 32;
m.optfile = 1;options nlp=convert;
Solve m using nlp minimizing obj;
display x.l, obj.l;
  


