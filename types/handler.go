package types

type HandleErrorType string

const (
	InvalidMethod = HandleErrorType("INVALID_METHOD")
	InvalidQuery  = HandleErrorType("INVALID_QUERY")
	NoResult      = HandleErrorType("NO_RESULT")
)

type HandleError struct {
	Error HandleErrorType
}
