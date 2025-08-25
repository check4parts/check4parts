import type { SupabaseClient } from '@supabase/supabase-js';

export type RestInPrice = {
	id?: string;
	provider: {
		id?: string;
		name: string;
		short_name?: string;
	};
	werehouse: {
		id?: string;
		name: string;
		short_name?: string;
	};
	quantity: number;
	delivery_time: string;
	price: number;
};

export async function restsInPrices(
	supabase: SupabaseClient,
	article: string,
	brand: string
): Promise<{ rests: RestInPrice[] }> {
	const { data: prices, error: pricesError } = await supabase
		.from('prices')
		.select(`*`)
		.eq('article', article)
		.textSearch('brand', `'${brand}'`, {
			type: 'websearch'
		});

	if (pricesError || !prices?.length) {
		console.error('Error fetching prices:', pricesError, prices);
		return { rests: [] };
	}

	const providerIds = new Set<string>();
	const warehouseIds = new Set<string>();

	for (const price of prices) {
		if (price.provider_id) providerIds.add(price.provider_id);
		if (price.rests && typeof price.rests === 'object') {
			Object.keys(price.rests).forEach((id) => warehouseIds.add(id));
		}
	}

	const { data: providers, error: providersError } = await supabase
		.from('providers')
		.select('*, warehouses(*)')
		.in('id', Array.from(providerIds));

	if (providersError || !providers) {
		console.error('Error fetching providers:', providersError?.message);
		return { rests: [] };
	}

	const providersMap = new Map<string, any>();
	const warehousesMap = new Map<string, any>();

	for (const provider of providers) {
		providersMap.set(provider.id, provider);
		for (const warehouse of provider.warehouses || []) {
			warehousesMap.set(warehouse.id, warehouse);
		}
	}

	const resultRests: RestInPrice[] = [];

	for (const priceEntry of prices) {
		const provider = providersMap.get(priceEntry.provider_id);
		const rests = priceEntry.rests;

		if (rests && typeof rests === 'object') {
			for (const warehouseId in rests) {
				if (!Object.prototype.hasOwnProperty.call(rests, warehouseId)) continue;

				const warehouse = warehousesMap.get(warehouseId);
				const quantity = parseInt(rests[warehouseId], 10);

				resultRests.push({
					id: priceEntry.id,
					provider: {
						id: provider?.id,
						name: provider?.name ?? 'Unknown Provider',
						short_name: provider?.short_name
					},
					werehouse: {
						id: warehouse?.id,
						name: warehouse?.name ?? 'Unknown Warehouse',
						short_name: warehouse?.short_name
					},
					quantity,
					delivery_time: priceEntry.delivery_time,
					price: priceEntry.price
				});
			}
		}
	}

	return { rests: resultRests };
}
