package models

import "errors"

type ProductCategory struct {
	CategoryName string `json:"category_name"`
}

func (cat ProductCategory) Validate() error {
	if cat.CategoryName == "" {
		return errors.New("category name can't be empty")
	}
	return nil
}
