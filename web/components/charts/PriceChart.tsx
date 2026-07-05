'use client';

import {
  AreaChart,
  Area,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
} from 'recharts';
import { ETFPrice } from '@/types/api';
import { formatCurrency, formatDateShort } from '@/lib/utils/formatters';
import { ETF_COLORS, CHART_CONFIG, CHART_COLORS } from '@/lib/utils/constants';

interface PriceChartProps {
  data: ETFPrice[];
  ticker: string;
  height?: number;
  showGrid?: boolean;
  animated?: boolean;
}

interface CustomTooltipProps {
  active?: boolean;
  payload?: Array<{ value: number }>;
  label?: string;
}

/**
 * Custom tooltip component with cyberpunk violet style.
 */
function CustomTooltip({ active, payload, label }: CustomTooltipProps) {
  if (!active || !payload || !payload.length) return null;

  return (
    <div
      className="rounded-lg p-3 backdrop-blur-sm animate-fade-in"
      style={{
        background: CHART_CONFIG.tooltipBg,
        border: `1px solid ${CHART_CONFIG.tooltipBorder}`,
        boxShadow: '0 0 20px -5px rgba(168, 85, 247, 0.3)',
      }}
    >
      <p className="text-xs text-muted-foreground mb-1">{label}</p>
      <p className="text-lg font-mono font-semibold text-violet-400">
        {formatCurrency(payload[0].value as number)}
      </p>
    </div>
  );
}

export function PriceChart({
  data,
  ticker,
  height = 350,
  showGrid = true,
  animated = true,
}: PriceChartProps) {
  const color = ETF_COLORS[ticker] || CHART_COLORS.primary;
  const gradientId = `gradient-${ticker}`;

  // Format data for Recharts
  const chartData = data.map((item) => ({
    date: item.date,
    price: item.close,
  }));

  return (
    <div className="w-full animate-fade-in">
      <ResponsiveContainer width="100%" height={height}>
        <AreaChart
          data={chartData}
          margin={{ top: 10, right: 10, left: 0, bottom: 0 }}
        >
          {/* Gradient definition */}
          <defs>
            <linearGradient id={gradientId} x1="0" y1="0" x2="0" y2="1">
              <stop
                offset="5%"
                stopColor={color}
                stopOpacity={CHART_CONFIG.gradientStart}
              />
              <stop
                offset="95%"
                stopColor={color}
                stopOpacity={CHART_CONFIG.gradientEnd}
              />
            </linearGradient>
          </defs>

          {/* Subtle grid */}
          {showGrid && (
            <CartesianGrid
              strokeDasharray="3 3"
              stroke={CHART_COLORS.grid}
              vertical={false}
            />
          )}

          {/* X Axis - dates */}
          <XAxis
            dataKey="date"
            tickFormatter={formatDateShort}
            tick={{ fontSize: 11, fill: CHART_CONFIG.axisColor }}
            tickLine={false}
            axisLine={false}
            dy={10}
            tickMargin={8}
          />

          {/* Y Axis - prices */}
          <YAxis
            tickFormatter={(value) => `$${value.toFixed(0)}`}
            tick={{ fontSize: 11, fill: CHART_CONFIG.axisColor }}
            tickLine={false}
            axisLine={false}
            domain={['auto', 'auto']}
            dx={-5}
            width={50}
          />

          {/* Custom tooltip */}
          <Tooltip
            content={<CustomTooltip />}
            cursor={{
              stroke: color,
              strokeOpacity: 0.3,
              strokeWidth: 1,
              strokeDasharray: '5 5',
            }}
          />

          {/* Area with gradient fill */}
          <Area
            type="monotone"
            dataKey="price"
            stroke={color}
            strokeWidth={CHART_CONFIG.strokeWidth}
            fill={`url(#${gradientId})`}
            dot={false}
            activeDot={{
              r: CHART_CONFIG.activeDotRadius,
              fill: color,
              stroke: '#19152A',
              strokeWidth: 2,
              style: {
                filter: `drop-shadow(0 0 6px ${color})`,
              },
            }}
            isAnimationActive={animated}
            animationDuration={1000}
            animationEasing="ease-out"
          />
        </AreaChart>
      </ResponsiveContainer>
    </div>
  );
}

/**
 * Mini version for dashboard cards.
 */
export function MiniPriceChart({
  data,
  ticker,
  height = 80,
}: Omit<PriceChartProps, 'showGrid' | 'animated'>) {
  const gradientId = `mini-gradient-${ticker}`;

  const chartData = data.slice(-30).map((item) => ({
    date: item.date,
    price: item.close,
  }));

  // Calculate trend
  const firstPrice = chartData[0]?.price || 0;
  const lastPrice = chartData[chartData.length - 1]?.price || 0;
  const isPositive = lastPrice >= firstPrice;
  const trendColor = isPositive ? CHART_COLORS.success : CHART_COLORS.danger;

  return (
    <div className="w-full">
      <ResponsiveContainer width="100%" height={height}>
        <AreaChart data={chartData} margin={{ top: 5, right: 0, left: 0, bottom: 0 }}>
          <defs>
            <linearGradient id={gradientId} x1="0" y1="0" x2="0" y2="1">
              <stop offset="5%" stopColor={trendColor} stopOpacity={0.2} />
              <stop offset="95%" stopColor={trendColor} stopOpacity={0} />
            </linearGradient>
          </defs>
          <Area
            type="monotone"
            dataKey="price"
            stroke={trendColor}
            strokeWidth={1.5}
            fill={`url(#${gradientId})`}
            dot={false}
            isAnimationActive={true}
            animationDuration={500}
          />
        </AreaChart>
      </ResponsiveContainer>
    </div>
  );
}
