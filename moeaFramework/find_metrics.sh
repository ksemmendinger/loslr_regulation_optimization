dirName="$1"
folderName="$2"
nseeds="$3"
nobjs="$4"

seeds=$(seq 1 ${nseeds})
JAVA_ARGS="-cp MOEAFramework-2.12-Demo.jar"

for s in ${seeds}
do

	java ${JAVA_ARGS} org.moeaframework.analysis.sensitivity.ResultFileEvaluator \
    -d ${nobjs} \
    -i "${dirName}"/"${folderName}"/moeaFramework/objs/runtime_S${s}.txt \
    -r "${dirName}"/"${folderName}"/moeaFramework/objRefset.txt \
    -o "${dirName}"/"${folderName}"/moeaFramework/metrics/runtime_S${s}.metrics \
    -f

    java ${JAVA_ARGS} org.moeaframework.analysis.sensitivity.ResultFileEvaluator \
    -d ${nobjs} \
    -i "${dirName}"/"${folderName}"/moeaFramework/objs/pareto_front_S${s}.txt \
    -r "${dirName}"/"${folderName}"/moeaFramework/objRefset.txt \
    -o "${dirName}"/"${folderName}"/moeaFramework/metrics/final_S${s}.metrics \
    -f

done