package utils

func Map[T1 any, T2 any](src []T1, fn func(T1) T2) []T2 {
	result := make([]T2, len(src))
	for idx, val := range src {
		result[idx] = fn(val)
	}
	return result
}

func EMap[T1 any, T2 any](src []T1, fn func(T1) (T2, error)) ([]T2, error) {
	result := make([]T2, len(src))
	var err error
	for idx, val := range src {
		result[idx], err = fn(val)
		if err != nil {
			return nil, err
		}
	}
	return result, nil
}

func Fold[T1 any, T2 any](src []T1, folder func(T2, T1) T2, acc T2) T2 {
	for _, v := range src {
		acc = folder(acc, v)
	}
	return acc
}

func Keys[T1 comparable, T2 any](m map[T1]T2) []T1 {
	result := make([]T1, 0, len(m))
	for k := range m {
		result = append(result, k)
	}
	return result
}
