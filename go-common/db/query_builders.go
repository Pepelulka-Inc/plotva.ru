package db

import (
	"fmt"
	"strings"
)

type WhereStatementBuilder struct {
	conditions []string
	args       []any
	offset     int
}

// offset is used for placeholders
func NewWhereStatementBuilder(offset int) *WhereStatementBuilder {
	return &WhereStatementBuilder{
		conditions: nil,
		args:       nil,
		offset:     offset,
	}
}

func (stb *WhereStatementBuilder) AddBasicConstraint(
	fieldName string,
	value any,
	constraint string, // can be "=", "<", ">" or smth like that
) {
	condition := fmt.Sprintf("%s %s $%d", fieldName, constraint, len(stb.args)+1+stb.offset)
	stb.conditions = append(stb.conditions, condition)
	stb.args = append(stb.args, value)
}

// Ограничение что какое то поле принадлежит элементу множества
func (stb *WhereStatementBuilder) AddSetConstraint(
	fieldName string,
	set []any,
	inverse bool,
) {
	var conditionBuilder strings.Builder
	if len(set) == 0 {
		return
	}

	conditionBuilder.WriteString(fieldName)
	if inverse {
		conditionBuilder.WriteString(" NOT IN (")
	} else {
		conditionBuilder.WriteString(" IN (")
	}

	for idx, val := range set {
		conditionBuilder.WriteString(fmt.Sprintf("$%d", len(stb.args)+1+stb.offset))
		stb.args = append(stb.args, val)
		if idx != len(set)-1 {
			conditionBuilder.WriteString(", ")
		}
	}
	conditionBuilder.WriteRune(')')
	stb.conditions = append(stb.conditions, conditionBuilder.String())
}

func (stb *WhereStatementBuilder) GetQuery() (string, []any) {
	if len(stb.conditions) == 0 {
		return "", nil
	}
	var builder strings.Builder
	builder.WriteString("WHERE ")
	for idx, cond := range stb.conditions {
		builder.WriteString(cond)
		if idx != len(stb.conditions)-1 {
			builder.WriteString(" AND ")
		}
	}
	return builder.String(), stb.args
}
