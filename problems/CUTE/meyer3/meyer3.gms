* GAMS-model meyer3.dag.gms written by dag2gams Converter at 29/03/2004 16:58:58
* University of Vienna
$offdigit;
 Set j/1*3/;
 Equations objcon
;
Variables x(j), obj;
* Objective function (to be minimized) 
objcon.. obj =e= power((exp(x('2') / (x('3') + 
50)) * x('1')) - 34780, 2) + 
power((exp(x('2') / (x('3') + 
55)) * x('1')) - 28610, 2) + 
power((exp(x('2') / (x('3') + 
60)) * x('1')) - 23650, 2) + 
power((exp(x('2') / (x('3') + 
65)) * x('1')) - 19630, 2) + 
power((exp(x('2') / (x('3') + 
70)) * x('1')) - 16370, 2) + 
power((exp(x('2') / (x('3') + 
75)) * x('1')) - 13720, 2) + 
power((exp(x('2') / (x('3') + 
80)) * x('1')) - 11540, 2) + 
power((exp(x('2') / (x('3') + 
85)) * x('1')) - 9744, 2) + 
power((exp(x('2') / (x('3') + 
90)) * x('1')) - 8261, 2) + 
power((exp(x('2') / (x('3') + 
95)) * x('1')) - 7030, 2) + 
power((exp(x('2') / (x('3') + 
100)) * x('1')) - 6005, 2) + 
power((exp(x('2') / (x('3') + 
105)) * x('1')) - 5147, 2) + 
power((exp(x('2') / (x('3') + 
110)) * x('1')) - 4427, 2) + 
power((exp(x('2') / (x('3') + 
115)) * x('1')) - 3820, 2) + 
power((exp(x('2') / (x('3') + 
120)) * x('1')) - 3307, 2) + 
power((exp(x('2') / (x('3') + 
125)) * x('1')) - 2872, 2);


Model m/All/;
m.workspace = 32;
m.optfile = 1;options nlp=convert;
Solve m using nlp minimizing obj;
display x.l, obj.l;
  


