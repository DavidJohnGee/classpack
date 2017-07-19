#!/bin/bash
echo "$1" | awk 'BEGIN {
    RS = "\n";
    FS = "\n"
}


{
    if (NR > 3) {
      n=split($1,array," ");
      if (array[1] != "") {
      	ints[array[1]] = sprintf("{\"name\": \"%s\", \"address\": \"%s\", \"state\": \"%s\"}",array[1], array[2], array[3]);
	int_count ++;
     }
    }

}

END {
	printf "\"[\n";
    	for (i in ints) {
          counter++;
    		printf "\t" ints[i];
		if (int_count - counter > 0) {
			printf ",\n";
		} else {
			printf "\n";
		}
	}
	print "]\"";
}'
