package main

import (
	"fmt"
	"math"
)

// maximumGap 求数组排序后相邻元素的最大差值
func maximumGap(nums []int) int {
	if len(nums) < 2 {
		return 0
	}

	// 找到数组中的最小值和最大值
	// 将minVal设置为系统最大，保证后续都比他小
	// maxVal设置为系统最小，保证后续都比他大
	minVal := math.MaxInt32
	maxVal := math.MinInt32
	for _, num := range nums {
		if num < minVal {
			minVal = num
		}
		if num > maxVal {
			maxVal = num
		}
	}

	// caculate the capacity of the bucket，make sure the min volume of the bucket is 1.
	bucketSize := int(math.Max(1, float64((maxVal-minVal)/(len(nums)-1))))
	fmt.Println("bucketSize = ", bucketSize)
	// caculate the amount of the bucket .
	// the reason why we add 1 is to make sure the result of the max and the min are not appear in a same buckey

	bucketNum := (maxVal-minVal)/bucketSize + 1
	fmt.Println("bucketNum = ", bucketNum)

	// create the bucket array ,every buctet contain the max and the min object.
	// init the buckets with maxVal and  minVal
	buckets := make([]struct{ Min, Max int }, bucketNum)
	for i := range buckets {
		buckets[i].Min = math.MaxInt32
		buckets[i].Max = math.MinInt32
	}

	// 将数字放入桶中
	for _, num := range nums {
		index := (num - minVal) / bucketSize
		fmt.Printf("num = %d,	index=%d \n",num,index)
		if num < buckets[index].Min {
			buckets[index].Min = num
		}
		if num > buckets[index].Max {
			buckets[index].Max = num
		}
	}
	for i,res:= range buckets{
		fmt.Printf("第%d个桶:max=%d , min=%d\n",i+1,res.Max,res.Min)
	} 
	// 计算相邻非空桶之间的最大差值
	prevMax := minVal
	maxGap := 0
	for _, bucket := range buckets {
		if bucket.Min == math.MaxInt32 && bucket.Max == math.MinInt32 {
			// 空桶，跳过
			continue
		}
		maxGap = int(math.Max(float64(maxGap), float64(bucket.Min-prevMax)))
		prevMax = bucket.Max
	}

	return maxGap
}

func main() {
	nums := []int{34, 12, 58, 2, 78, 43, 91, 23, 15, 87, 10, 51, 94, 31, 66, 19, 8, 72, 37, 63}
	maxGap := maximumGap(nums)
	fmt.Println("Maximum gap:", maxGap)
}
