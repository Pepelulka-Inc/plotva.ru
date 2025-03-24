package kafka

import (
	"encoding/json"

	"github.com/IBM/sarama"
)

type KafkaConfig struct {
	Brokers  []string `yaml:"brokers"`
	MaxRetry int      `yaml:"max_retry"`
}

const KafkaProductViewsTopicName string = "product_views"

type KafkaProducer struct {
	producer sarama.SyncProducer
}

func NewProducer(cfg KafkaConfig) (*KafkaProducer, error) {
	config := sarama.NewConfig()
	config.Producer.RequiredAcks = sarama.WaitForAll
	config.Producer.Retry.Max = cfg.MaxRetry
	config.Producer.Return.Successes = true
	producer, err := sarama.NewSyncProducer(cfg.Brokers, config)
	return &KafkaProducer{producer}, err
}

func (p *KafkaProducer) Close() error {
	return p.producer.Close()
}

func (p *KafkaProducer) SendString(topic string, content string) error {
	msg := sarama.ProducerMessage{
		Topic: topic,
		Value: sarama.StringEncoder(content),
	}
	_, _, err := p.producer.SendMessage(&msg)
	return err
}

func (p *KafkaProducer) SendJSON(topic string, content any) error {
	body, err := json.Marshal(content)
	if err != nil {
		return err
	}
	msg := sarama.ProducerMessage{
		Topic: topic,
		Value: sarama.ByteEncoder(body),
	}
	_, _, err = p.producer.SendMessage(&msg)
	return err
}
