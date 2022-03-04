odoo.define("carmarge_cn.product", function (require) {
    'use strict';

    var BasicModel  = require("web.BasicModel");

    const AGGREGATABLE_TYPES = ['float', 'integer', 'monetary'];

    BasicModel.include({
        _readGroup: function (list, options) {
            var self = this;
            options = options || {};
            var groupByField = list.groupedBy[0];
            var rawGroupBy = groupByField.split(':')[0];
            var fields = _.uniq(list.getFieldNames().concat(rawGroupBy));
            var orderedBy = _.filter(list.orderedBy, function (order) {
                return order.name === rawGroupBy || list.fields[order.name].group_operator !== undefined;
            });
            var openGroupsLimit = list.groupsLimit || self.OPEN_GROUP_LIMIT;
            var expand = list.openGroupByDefault && options.fetchRecordsWithGroups;
            return this._rpc({
                    model: list.model,
                    method: 'web_read_group',
                    fields: fields,
                    domain: list.domain,
                    context: list.context,
                    groupBy: list.groupedBy,
                    limit: list.groupsLimit,
                    offset: list.groupsOffset,
                    orderBy: orderedBy,
                    lazy: true,
                    expand: expand,
                    expand_limit: expand ? list.limit : null,
                    expand_orderby: expand ? list.orderedBy : null,
                })
                .then(function (result) {
                    var groups = result.groups;
                    list.groupsCount = result.length;
                    var previousGroups = _.map(list.data, function (groupID) {
                        return self.localData[groupID];
                    });
                    list.data = [];
                    list.count = 0;
                    var defs = [];
                    var openGroupCount = 0;
    
                    _.each(groups, function (group) {
                        var aggregateValues = {};
                        for (var key in group){
                            var value = group[key];
                            if (_.contains(fields, key) && key !== groupByField &&
                                AGGREGATABLE_TYPES.includes(list.fields[key].type)) {
                                    aggregateValues[key] = value;
                            }
                        }
                        // _.each(group, function (value, key) {
                            // console.log(key)
                            // if (_.contains(fields, key) && key !== groupByField &&
                            //     AGGREGATABLE_TYPES.includes(list.fields[key].type)) {
                            //         aggregateValues[key] = value;
                            // }
                        // });
                        // When a view is grouped, we need to display the name of each group in
                        // the 'title'.
                        var value = group[groupByField];
                        if (list.fields[rawGroupBy].type === "selection") {
                            var choice = _.find(list.fields[rawGroupBy].selection, function (c) {
                                return c[0] === value;
                            });
                            value = choice ? choice[1] : false;
                        }
                        var newGroup = self._makeDataPoint({
                            modelName: list.model,
                            count: group[rawGroupBy + '_count'],
                            domain: group.__domain,
                            context: list.context,
                            fields: list.fields,
                            fieldsInfo: list.fieldsInfo,
                            value: value,
                            aggregateValues: aggregateValues,
                            groupedBy: list.groupedBy.slice(1),
                            orderedBy: list.orderedBy,
                            orderedResIDs: list.orderedResIDs,
                            limit: list.limit,
                            openGroupByDefault: list.openGroupByDefault,
                            parentID: list.id,
                            type: 'list',
                            viewType: list.viewType,
                        });
                        var oldGroup = _.find(previousGroups, function (g) {
                            return g.res_id === newGroup.res_id && g.value === newGroup.value;
                        });
                        if (oldGroup) {
                            delete self.localData[newGroup.id];
                            // restore the internal state of the group
                            var updatedProps = _.pick(oldGroup, 'isOpen', 'offset', 'id');
                            if (options.onlyGroups || oldGroup.isOpen && newGroup.groupedBy.length) {
                                // If the group is opened and contains subgroups,
                                // also keep its data to keep internal state of
                                // sub-groups
                                // Also keep data if we only reload groups' own data
                                updatedProps.data = oldGroup.data;
                                if (options.onlyGroups) {
                                    // keep count and res_ids as in this case the group
                                    // won't be search_read again. This situation happens
                                    // when using kanban quick_create where the record is manually
                                    // added to the datapoint before getting here.
                                    updatedProps.res_ids = oldGroup.res_ids;
                                    updatedProps.count = oldGroup.count;
                                }
                            }
                            _.extend(newGroup, updatedProps);
                            // set the limit such that all previously loaded records
                            // (e.g. if we are coming back to the kanban view from a
                            // form view) are reloaded
                            newGroup.limit = oldGroup.limit + oldGroup.loadMoreOffset;
                            self.localData[newGroup.id] = newGroup;
                        } else if (!newGroup.openGroupByDefault || openGroupCount >= openGroupsLimit) {
                            newGroup.isOpen = false;
                        } else if ('__fold' in group) {
                            newGroup.isOpen = !group.__fold;
                        } else {
                            // open the group iff it is a first level group
                            newGroup.isOpen = !self.localData[newGroup.parentID].parentID;
                        }
                        list.data.push(newGroup.id);
                        list.count += newGroup.count;
                        if (newGroup.isOpen && newGroup.count > 0) {
                            openGroupCount++;
                            if (group.__data) {
                                // bypass the search_read when the group's records have been obtained
                                // by the call to 'web_read_group' (see @_searchReadUngroupedList)
                                newGroup.__data = group.__data;
                            }
                            options = _.defaults({enableRelationalFetch: false}, options);
                            defs.push(self._load(newGroup, options));
                        }
                    });
                    if (options.keepEmptyGroups) {
                        // Find the groups that were available in a previous
                        // readGroup but are not there anymore.
                        // Note that these groups are put after existing groups so
                        // the order is not conserved. A sort *might* be useful.
                        var emptyGroupsIDs = _.difference(_.pluck(previousGroups, 'id'), list.data);
                        _.each(emptyGroupsIDs, function (groupID) {
                            list.data.push(groupID);
                            var emptyGroup = self.localData[groupID];
                            // this attribute hasn't been updated in the previous
                            // loop for empty groups
                            emptyGroup.aggregateValues = {};
                        });
                    }
    
                    return Promise.all(defs).then(function (groups) {
                        if (!options.onlyGroups) {
                            // generate the res_ids of the main list, being the concatenation
                            // of the fetched res_ids in each group
                            list.res_ids = _.flatten(_.map(groups, function (group) {
                                return group ? group.res_ids : [];
                            }));
                        }
                        return list;
                    }).then(function () {
                        return Promise.all([
                            self._fetchX2ManysSingleBatch(list),
                            self._fetchReferencesSingleBatch(list)
                        ]).then(function () {
                            return list;
                        });
                    });
                });
        },
    });
    
});