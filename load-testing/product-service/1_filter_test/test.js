import http from 'k6/http';
import { check, sleep } from 'k6';
import { randomItem, randomIntBetween } from 'https://jslib.k6.io/k6-utils/1.4.0/index.js';

const URL = 'http://localhost:8080/api/product/filter';
const CATS_DATA = './data/categories.json'
const SELLERS_DATA = './data/sellers.json'

const CATS_IN_FILTER_COUNT = 10
const SELLERS_IN_FILTER_COUNT = 10

export let options = {
    stages: [
        { duration: '10s', target: 1000 },  // Разгон до 1000 пользователей
        { duration: '20s', target: 1000 },  // Держим нагрузку 1000 пользователей
    ],
    thresholds: {
        http_req_duration: ['p(95)<500'], // 95% запросов должны быть быстрее 500 мс
        http_reqs: ['rate>100'], // Минимальный RPS
    },
};

const cats = JSON.parse(open(CATS_DATA));
const sellers = JSON.parse(open(SELLERS_DATA));

function generateRandomFilter() {
    return JSON.stringify({
        min_price: randomIntBetween(1, 100000),
        max_price: randomIntBetween(1, 100000),
        categories_list: Array.from(
            {length: CATS_IN_FILTER_COUNT},
            () => randomItem(cats)
        ),
        sellers_id_list: Array.from(
            {length: SELLERS_IN_FILTER_COUNT},
            () => randomItem(sellers)
        )
    });
}

export default function () {
    let payload = generateRandomFilter();
    let params = { headers: { 'Content-Type': 'application/json' } };
    
    let res = http.post(URL, payload, params);
    
    check(res, {
        'is status 200': (r) => r.status === 200,
        'response time < 500ms': (r) => r.timings.duration < 500,
    });
    
    sleep(0.1); // Задержка между запросами
}
