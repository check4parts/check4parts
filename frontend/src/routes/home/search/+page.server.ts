import { restsInPrices } from '$lib/utils/adapter/restsInPrices';
import type { PageServerLoad } from './$types';

export const load: PageServerLoad = async ({ url, locals: { supabaseTecdoc: supabase, supabasePrices } }) => {
	const searchQuery = url.searchParams.get('q');

	let partsPromise: Promise<any[]>;

	if (searchQuery) {
		partsPromise = (async () => {
			const { data: articlesData, error: articlesError } = await supabase
				.from('articles')
				.select(
					`
          id,
          "DataSupplierArticleNumber",
          "NormalizedDescription",
          "Description",
          suppliers (
            id,
            "MatchCode",
            "Description"
          )
        `
				)
				.eq('DataSupplierArticleNumber', searchQuery)
				.limit(50);

			if (articlesError) {
				console.error('Error fetching articles for search:', articlesError);
				throw new Error('Failed to perform search: ' + articlesError.message);
			}


			if (articlesData) {
				return articlesData.map((article) => ({
					name: article.NormalizedDescription || 'Без опису',
					description: article.Description || article.NormalizedDescription || 'Без опису',
					brand: article.suppliers?.MatchCode || 'Невідомий бренд',
					details: [],
					id: article.DataSupplierArticleNumber || 'N/A',
					code: article.id?.toString() || '',
					image: '/image 7.png',
					rests: restsInPrices(supabasePrices, article.DataSupplierArticleNumber, article.suppliers?.MatchCode)
				}));
			}
			return [];
		})();
	} else {
		partsPromise = Promise.resolve([]);
	}

	return {
		searchQuery,
		parts: partsPromise
	};
};
