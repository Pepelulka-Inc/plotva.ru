package hu

type BasicResponse struct {
	Status  string `json:"status"`
	Message string `json:"message"`
}

func Ok() BasicResponse {
	return BasicResponse{
		Status:  "ok",
		Message: "",
	}
}

func Error(err error) BasicResponse {
	return BasicResponse{
		Status:  "error",
		Message: err.Error(),
	}
}

func ErrorStr(str string) BasicResponse {
	return BasicResponse{
		Status:  "error",
		Message: str,
	}
}
