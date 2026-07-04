'use client';

import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
} from 'recharts';
import { ETFPrice } from '@/types/api';
import { formatCurrency, formatDateShort } from '@/lib/utils/formatters';
import { ETF_COLORS } from '@/lib/utils/constants';

interface PriceChartProps {
  data: ETFPrice[];
  ticker: string;
  height?: number;
}

export function PriceChart({ data, ticker, height = 300 }: PriceChartProps) {
  const color = ETF_COLORS[ticker] || '#3B82F6';

  // Formatter les données pour Recharts
  const chartData = data.map((item) => ({
    date: item.date,
    price: item.close,
  }));

  return (
    <ResponsiveContainer width="100%" height={height}>
      <LineChart data={chartData}>
        <CartesianGrid strokeDasharray="3 3" className="stroke-muted" />
        <XAxis
          dataKey="date"
          tickFormatter={formatDateShort}
          tick={{ fontSize: 12 }}
          tickLine={false}
          axisLine={false}
        />
        <YAxis
          tickFormatter={(value) => `$${value.toFixed(0)}`}
          tick={{ fontSize: 12 }}
          tickLine={false}
          axisLine={false}
          domain={['auto', 'auto']}
        />
        <Tooltip
          content={({ active, payload, label }) => {
            if (active && payload && payload.length) {
              return (
                <div className="bg-background border rounded-lg shadow-lg p-3">
                  <p className="text-sm text-muted-foreground">{label}</p>
                  <p className="text-sm font-medium">
                    {formatCurrency(payload[0].value as number)}
                  </p>
                </div>
              );
            }
            return null;
          }}
        />
        <Line
          type="monotone"
          dataKey="price"
          stroke={color}
          strokeWidth={2}
          dot={false}
          activeDot={{ r: 4 }}
        />
      </LineChart>
    </ResponsiveContainer>
  );
}
