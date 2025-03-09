package models

import (
	"time"

	jt "plotva.ru/common/json_types"
)

type Product struct {
	ProductID    jt.JsonUUID `json:"product_id"`
	Name         string      `json:"name"`
	Description  string      `json:"description"`
	SellerID     jt.JsonUUID `json:"seller_id"`
	Category     string      `json:"category"`
	PhotoURL     string      `json:"photo_url"`
	PriceRub     int         `json:"price_rub"`
	CreationTime time.Time   `json:"creation_time"`
}

type ProductCreate struct {
	Name        string      `json:"name" validate:"required"`
	Description string      `json:"description" validate:"required"`
	SellerID    jt.JsonUUID `json:"seller_id" validate:"required"`
	Category    string      `json:"category" validate:"required"`
	PhotoURL    string      `json:"photo_url" validate:"required"`
	PriceRub    int         `json:"price_rub" validate:"required"`
}

// Фильтр для запросов по товарам
type ProductFilter struct {
	// Поля сделаны указателями, чтобы можно было указывать nil значение
	MinPrice        *int          `json:"min_price,omitempty"`
	MaxPrice        *int          `json:"max_price,omitempty"`
	CategoriesList  []string      `json:"categories_list,omitempty"`
	NameFilter      *string       `json:"name_filter,omitempty"`
	SellersIDList   []jt.JsonUUID `json:"sellers_id_list,omitempty"`
	MinCreationTime *time.Time    `json:"min_creation_time,omitempty"`
	MaxCreationTime *time.Time    `json:"max_creation_time,omitempty"`
}
