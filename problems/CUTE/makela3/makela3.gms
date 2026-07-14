* GAMS-model makela3.dag.gms written by dag2gams Converter at 29/03/2004 16:59:59
* University of Vienna
$offdigit;
 Set i/1*20/;
 Set j/1*21/;
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
con18
con19
con20
;
Variables x(j), obj;
* Objective function (to be minimized) 
objcon.. obj =e= x('21');


con1..-x('21') + 
power(x('1'), 2) =l= 0;
con2..-x('21') + 
power(x('2'), 2) =l= 0;
con3..-x('21') + 
power(x('20'), 2) =l= 0;
con4..-x('21') + 
power(x('3'), 2) =l= 0;
con5..-x('21') + 
power(x('4'), 2) =l= 0;
con6..-x('21') + 
power(x('5'), 2) =l= 0;
con7..-x('21') + 
power(x('19'), 2) =l= 0;
con8..-x('21') + 
power(x('6'), 2) =l= 0;
con9..-x('21') + 
power(x('7'), 2) =l= 0;
con10..-x('21') + 
power(x('8'), 2) =l= 0;
con11..-x('21') + 
power(x('18'), 2) =l= 0;
con12..-x('21') + 
power(x('9'), 2) =l= 0;
con13..-x('21') + 
power(x('10'), 2) =l= 0;
con14..-x('21') + 
power(x('11'), 2) =l= 0;
con15..-x('21') + 
power(x('17'), 2) =l= 0;
con16..-x('21') + 
power(x('12'), 2) =l= 0;
con17..-x('21') + 
power(x('13'), 2) =l= 0;
con18..-x('21') + 
power(x('14'), 2) =l= 0;
con19..-x('21') + 
power(x('16'), 2) =l= 0;
con20..-x('21') + 
power(x('15'), 2) =l= 0;
Model m/All/;
m.workspace = 32;
m.optfile = 1;options nlp=convert;
Solve m using nlp minimizing obj;
display x.l, obj.l;
  


