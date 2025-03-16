package jt

import (
	"encoding/json"

	"github.com/google/uuid"
)

type JsonUUID uuid.UUID

func (u JsonUUID) MarshalJSON() ([]byte, error) {
	return json.Marshal(uuid.UUID(u).String())
}

func (u *JsonUUID) UnmarshalJSON(data []byte) error {
	var str string
	if err := json.Unmarshal(data, &str); err != nil {
		return err
	}
	parsedUUID, err := uuid.Parse(str)
	if err != nil {
		return err
	}
	*u = JsonUUID(parsedUUID)
	return nil
}
