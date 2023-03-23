from spex.model.document import DocumentParser


# class ZndFig48(BytesTableExtractor):
#     def data_extract(self, row: "Element") -> "Element":
#         return Xpath.elem_first_req(row, "./td[3]")
#
#
# class ZndFig50(BytesTableExtractor):
#     def data_extract(self, row: "Element") -> "Element":
#         return Xpath.elem_first_req(row, "./td[3]")


class NvmCsZoned11c(DocumentParser):

    label_overrides = {
        ("37", "0"): "zt",
        ("37", "1"): "zs",
        ("37", "2"): "za",
    }

    fig_extractor_overrides = {
        # "48": ZndFig48,
        # "50": ZndFig50,
    }
